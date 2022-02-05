# coding:utf-8
import re
import time
import json
import logger
import requests
import login_manager

headers = {
    'user-agent':
    r'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 Edg/97.0.4692.99'
}


def _to_formdata(json_obj):
    formdata = {}
    for key in json_obj:
        formdata[key] = (None, json_obj[key])
    return formdata


def is_bilibili_host(url):
    matched = re.match(r'\w+:\/\/.*\.bili\w+\.com[\/]?.*',
                       url,
                       flags=re.IGNORECASE)
    return None != matched


def check_if_movie_exists_in_official_site(movie_name):
    logger.log_debug(f'Input movie_name: {movie_name}')
    response = requests.get(
        url=
        fr'https://api.bilibili.com/x/web-interface/search/type?search_type=media_ft&keyword={movie_name}',
        cookies={'Cookie': login_manager.get_cookies()},
        headers=headers)
    text = response.content.decode('utf-8')
    response = json.loads(text)
    logger.log_debug(f'Response from bilibili search api: {text}')
    if 'code' not in response:
        logger.log_error('No `code` in response json.')
        return False

    code = response['code']
    if 0 != code:
        logger.log_error(
            f'Unable to search this movie from bilibili official site, code: {code}'
        )
        return False

    if 'data' not in response:
        logger.log_error('No `data` in response json.')
        return False

    data = response['data']
    if 'result' not in data:
        logger.log_debug(
            f'No this movie {movie_name} in bilibili official site.')
        return False

    result = data['result']
    if len(result) == 0:
        logger.log_debug(
            f'No this movie {movie_name} in bilibili official site.')
        return False

    for e in result:
        matched = re.match(fr'.*{movie_name}.*', e['title'])
        if None != matched:
            return True

    return False


def start_live(room_id=3790580):
    try:
        data = {
            'csrf': (None, login_manager.get_csrf()),
            'csrf_token': (None, login_manager.get_csrf_token()),
            'area_v2': (None, '33'),
            'platform': (None, 'pc'),
            'room_id': (None, room_id),
        }
        response = requests.post(
            url=fr'https://api.live.bilibili.com/room/v1/Room/startLive',
            cookies={'Cookie': login_manager.get_cookies()},
            headers=headers,
            files=data)
        response = response.content.decode('utf-8')
        response = json.loads(response)

        return response

    except Exception as ex:
        logger.log_error(f'Unable to get websocket url, {ex}')
        return ''


def get_real_room_id(room_id=3790580):
    try:
        response = requests.get(
            url=
            fr'https://api.live.bilibili.com/room/v1/Room/room_init?id={room_id}',
            cookies={'Cookie': login_manager.get_cookies()},
            headers=headers)
        response = response.content.decode(encoding='utf-8')
        response = json.loads(response)

        if 'data' not in response:
            return (room_id, room_id)
        data = response['data']

        if 'room_id' not in data:
            return (room_id, room_id)

        return (data['room_id'], data['uid'])

    except Exception as ex:
        logger.log_error(f'Unable to get websocket url, {ex}')
        return ''


def get_room_websocket_url(room_id=3790580):
    try:
        response = requests.get(
            url=
            fr'https://api.live.bilibili.com/room/v1/Danmu/getConf?room_id={room_id}&platform=pc&player=web',
            cookies={'Cookie': login_manager.get_cookies()},
            headers=headers)

        response = response.content.decode('utf-8')

        response = json.loads(response)

        if 'data' not in response:
            return ('', '')
        data = response['data']

        if 'token' not in data:
            return ('', '')
        token = data['token']

        if 'host_server_list' not in data:
            return ('', '')
        host_server_list = data['host_server_list']

        if 0 == len(host_server_list):
            return ('', '')
        host_server = host_server_list[0]

        if 'host' not in host_server or 'port' not in host_server:
            return ('', '')
        host = host_server['host']
        port = host_server['wss_port']

        return (f'wss://{host}:{port}/sub', token)

    except Exception as ex:
        logger.log_error(f'Unable to get websocket url, {ex}')
        return ('', '')

    pass


def send_danmu_message(room_id, message):
    try:
        data = {
            "bubble": 0,
            "msg": message,
            "color": 16777215,
            "mode": 1,
            "fontsize": 25,
            "rnd": int(time.time()),
            "roomid": room_id,
            "csrf": login_manager.get_csrf(),
            "csrf_token": login_manager.get_csrf_token(),
        }
        formdata = _to_formdata(data)
        response = requests.post(
            url=r'https://api.live.bilibili.com/msg/send',
            cookies={'Cookie': login_manager.get_cookies()},
            headers=headers,
            files=formdata)
        response = response.content.decode('utf-8')
        logger.log_debug(f'Send message, response: {response}')
    except Exception as ex:
        logger.log_error(f'Unable to send message, {ex}')
        return