# coding:utf-8
import json
import time
import brotli
import logger
import threading
import bilibili_http_api
from websocket import WebSocketApp
"""
头部格式：
偏移量    长度   类型       含义
0          4     int     数据包总长度
4          2     int     数据包头部长度
6          2     int     数据包协议版本
8          4     int     数据包类型
12         4     int     取常数1
16         -     bytes[] 数据主体


数据包协议版本        含义
0                  数据包有效负载为未压缩的JSON格式数据
1                  客户端心跳包，或服务器心跳回应（带有人气值）
3                  数据包有效负载为通过br压缩后的JSON格式数据（之前是zlib）


数据包类型  发送方       名称             含义
2           Client     心跳             不发送心跳包，50-60秒后服务器会强制断开连接
3           Server     心跳回应         有效负载为直播间人气值
5           Server     通知             有效负载为礼物、弹幕、公告等内容数据
7           Client     认证（加入房间） 客户端成功建立连接后发送的第一个数据包
8           Server     认证成功回应     服务器接受认证包后回应的第一个数据包



客户端建立连接后，需要在5秒内发出加入房间（认证）的数据包，否则会被服务器强制断开连接。
其中有效负载的key字段内容可以从之前的 https://api.live.bilibili.com/room/v1/Danmu/getConf?room_id=房间号&platform=pc&player=web 获取。
如发送的认证包格式错误，服务器会立刻强制断开连接。
下面为认证数据包主体JSON字段的详细说明见下表。
字段          类型       含义
uid          number     用户uid
roomid        number     房间号
protover       number     协议版本，目前为3
platform       string     平台
type          number     不清楚，填2
key          string     应该是接口返回的token值，测试时值为空字符串也可以 作者：鱼肉烧 https://www.bilibili.com/read/cv14101053/ 出处：bilibili
"""

headers = {
    'user-agent':
    r'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 Edg/97.0.4692.99',
}


def _unsigned_integer_to_bytes(integer, size):
    return integer.to_bytes(size, byteorder='big', signed=False)


def _uint8_to_bytes(n):
    return _unsigned_integer_to_bytes(n, 1)


def _uint16_to_bytes(n):
    return _unsigned_integer_to_bytes(n, 2)


def _uint32_to_bytes(n):
    return _unsigned_integer_to_bytes(n, 4)


def _bytes_to_unsigned_integer(b):
    return int.from_bytes(b, 'big', signed=False)


def _bytes_to_uint8(b, offset=0):
    buffer = b[offset:offset + 1]
    return _bytes_to_unsigned_integer(buffer)


def _bytes_to_uint16(b, offset=0):
    buffer = b[offset:offset + 2]
    return _bytes_to_unsigned_integer(buffer)


def _bytes_to_uint32(b, offset=0):
    buffer = b[offset:offset + 4]
    return _bytes_to_unsigned_integer(buffer)


class live_message_manager(object):
    def __init__(self, room_id) -> None:
        (self.room_id, self.uid) = bilibili_http_api.get_real_room_id(room_id)
        (self.url,
         self.token) = bilibili_http_api.get_room_websocket_url(self.room_id)
        self.ws = None
        self.alive = False
        self.heart_beat_thread = None
        pass

    def _encode_message(version, op, body=b''):
        body_size = len(body)
        result_bytes = b''
        result_bytes += _uint32_to_bytes(body_size + 16)
        result_bytes += _uint16_to_bytes(16)  # 数据包头长度
        result_bytes += _uint16_to_bytes(version)  # 数据包协议版本
        result_bytes += _uint32_to_bytes(op)  # 数据包类型
        result_bytes += _uint32_to_bytes(1)
        result_bytes += body
        return result_bytes

    def _encode_heart_beat_message():
        return live_message_manager._encode_message(1, 2)

    def _encode_authentication_message(message):
        return live_message_manager._encode_message(0, 7, message.encode())

    def _decode_message(message_bytes):
        package_length = _bytes_to_uint32(message_bytes, 0)
        header_length = _bytes_to_uint16(message_bytes, 4)
        version = _bytes_to_uint16(message_bytes, 6)
        type = _bytes_to_uint16(message_bytes, 8)

        message = message_bytes[header_length:]

        if 0 == version:
            message = message.decode('utf-8')
            message = json.loads(message)
        elif 3 == version:
            message = brotli.decompress(message)
            message = live_message_manager._decode_message(message)
        else:
            return None

        logger.log_debug(
            f'message_size: {package_length - header_length}, version: {version}, type: {type}, message: {message}'
        )

        return message

    def _user_entered(self, uname):
        logger.log_debug(f'[USER_IN] 欢迎 {uname} 进入直播间！')
        pass

    def _danmu_message(self, message):
        logger.log_debug(f'[DANMU_MSG] 弹幕消息：{message}')
        pass

    def _send_gift(self, uname, action, gift_name, gift_count):
        message = f'感谢{uname}{action}{gift_name}x{gift_count}'
        logger.log_debug(f'[SEND_GIFT] {message}')
        bilibili_http_api.send_danmu_message(self.room_id, message)
        pass

    def _system_message(self, data):
        logger.log_debug(f'[SYS_MSG] {data}')

    def _on_connect(self, base):
        logger.log_debug('On websocket connected.')

        request_json = {
            "uid": self.uid,
            "roomid": self.room_id,
            "protover": 3,
            "platform": "web",
            "type": 2,
            "key": self.token
        }
        try:
            request_json = json.dumps(request_json)
            request_bytes = live_message_manager._encode_authentication_message(
                request_json)
            self.ws.send(request_bytes)
            self.alive = True
            self.heart_beat_thread = threading.Thread(target=self._run)
            self.heart_beat_thread.start()
        except Exception as ex:
            logger.log_error(
                f'Unable to send connect message to {self.url}, {ex}')
        pass

    def _on_message(self, base, message_bytes):
        logger.log_debug(f'On websocket message arrived.')
        message = live_message_manager._decode_message(message_bytes)
        if None != message:
            if 'cmd' not in message:
                logger.log_error('No `cmd` in message.')
                return
            cmd = message['cmd']

            if 'data' not in message:
                logger.log_error('No `data` in message.')
                return
            data = message['data']

            if 'INTERACT_WORD' == cmd:
                self._user_entered(data['uname'])
                return
            if 'DANMU_MSG' == cmd:
                self._danmu_message(data['info'][1])
                return
            if 'SEND_GIFT' == cmd:
                self._send_gift(data['uname'], data['action'],
                                data['giftName'], data['num'])
                return
            if 'SYS_MSG' == cmd:
                self._system_message(data)
                return
            pass
        pass

    def _on_close(self, base, status_code, message):
        logger.log_debug(
            f'On websocket closed, status_code: {status_code}, message: {message}'
        )
        self.alive = False
        self.heart_beat_thread = None
        time.sleep(5)
        self.start()
        pass

    def _on_error(self, base, ex):
        logger.log_debug(f'On websocket error: {ex}.')
        pass

    def _on_ping(self, base, message):
        logger.log_debug(f'On websocket ping, message: {message}.')
        pass

    def _on_pong(self, base, message):
        logger.log_debug(f'On websocket pong, message: {message}.')
        pass

    def _run(self):
        while self.alive:
            message = live_message_manager._encode_heart_beat_message()
            self.ws.send(message)
            time.sleep(30)
        pass

    def start(self):
        # websocket.enableTrace(True)  # 开启运行状态追踪， debug 的时候最好打开他，便于追踪定位问题。

        self.ws = WebSocketApp(self.url,
                               header=headers,
                               on_open=self._on_connect,
                               on_message=self._on_message,
                               on_error=self._on_error,
                               on_close=self._on_close)

        self.ws.run_forever()

        pass


def startup():
    live_message_manager(3790580).start()
    pass