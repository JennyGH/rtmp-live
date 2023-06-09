# coding:utf-8
import os
import time
import ffmpy3
import ffmpeg
import platform

import logger
import last_play_record_manager


def _get_seconds_from_time_string(val):
    if '' == val:
        return 0
    splited = val.split(':')
    h = int(splited[0], base=10)
    m = int(splited[1], base=10)
    s = int(splited[2], base=10)
    return h * 60 * 60 + m * 60 + s


class basic_media_player(object):
    def __init__(self, root, rtmp_url) -> None:
        super().__init__()
        self.root = root
        self.rtmp_url = rtmp_url
        pass

    def _is_a_valid_media_file(self, path):
        if '' == path:
            return False
        if not os.path.exists(path):
            return False
        if not os.path.isfile(path):
            return False
        try:
            probe = ffmpeg.probe(path)
            return 'streams' in probe
        except Exception:
            return False

    def _try_play(self, ff):
        try:
            if platform.system() == 'Linux':
                ff.run()
            else:
                ff.run()
                # time.sleep(1)
            return True
        except:
            return False

    def _play(self, in_path, play_option):
        draw_text = play_option['draw_text']
        logger.log_debug(f'Play {in_path}')
        start_ticks = 0
        end_ticks = 0
        start_time = last_play_record_manager.get_start_time()
        if '00:00:00' == start_time and '' != play_option['start_time']:
            start_time = play_option['start_time']
        total_seconds = _get_seconds_from_time_string(start_time)
        end_time = play_option['end_time']
        if '' != end_time:
            start_seconds = _get_seconds_from_time_string(start_time)
            end_seconds = _get_seconds_from_time_string(end_time)
            if start_seconds > end_seconds:
                return
            end_time = f'-to {end_time}'
        while True:
            ss = "-ss " + start_time
            last_play_record_manager.set_start_time(start_time)
            ff = ffmpy3.FFmpeg(
                global_options=["-re", end_time],
                inputs={in_path: f"{ss}"},
                outputs={
                    self.rtmp_url:
                    "-c:a aac -b:v 3000k -f flv -preset fast -max_muxing_queue_size 1024 -rw_timeout 300000 "
                    +
                    (f"-c:v libx264 -vf drawtext=fontcolor=white:fontsize=20:bordercolor=black:borderw=2:text='{draw_text}':x=10:y=10"
                     if '' != draw_text else "-c:v copy")
                })
            logger.log_debug(ff.cmd)

            # 如果 开始时间 和 结束时间 相等，说明是从头开始播放的，记录开始时间
            ticks_1 = time.time()
            if 0 == start_ticks:
                start_ticks = ticks_1
            success = self._try_play(ff)
            ticks_2 = time.time()
            now_ticks = ticks_2
            # 如果播放失败了
            if not success:
                diff_sec = ticks_2 - ticks_1
                if (diff_sec > 60 * 2):
                    end_ticks = now_ticks
                    during_seconds = end_ticks - start_ticks
                    total_seconds += during_seconds
                    m, s = divmod(total_seconds, 60)
                    h, m = divmod(m, 60)
                    start_time = ("%02d:%02d:%02d" % (h, m, s))
            else:
                break

    def startup(self):
        pass