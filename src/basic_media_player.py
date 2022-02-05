# coding:utf-8
import os
import time
import ffmpy3
import ffmpeg
import platform

import logger


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

    def _play(self, in_path, draw_text=''):
        logger.log_debug(f'Play {in_path}')
        start_ticks = 0
        end_ticks = 0
        while True:
            during_seconds = end_ticks - start_ticks
            m, s = divmod(during_seconds, 60)
            h, m = divmod(m, 60)
            ss = "-ss " + ("%02d:%02d:%02d" % (h, m, s))
            ff = ffmpy3.FFmpeg(
                global_options=["-re"],
                inputs={in_path: f"{ss}"},
                outputs={
                    self.rtmp_url:
                    fr"-c:a aac -c:v libx264 -b:v 3000k -f flv -vf drawtext=fontcolor=white:fontsize=20:bordercolor=black:borderw=2:text='{draw_text}':x=10:y=10"
                    if '' != draw_text else
                    "-c:a aac -c:v copy -b:v 3000k -f flv -tune zerolatency -preset fast"
                })
            logger.log_debug(ff.cmd)

            # 如果 开始时间 和 结束时间 相等，说明是从头开始播放的，记录开始时间
            ticks_1 = time.time()
            if end_ticks == start_ticks:
                start_ticks = ticks_1
            success = self._try_play(ff)
            ticks_2 = time.time()
            now_ticks = ticks_2
            # 如果播放失败了
            if not success:
                if (ticks_2 - ticks_1 > 60 * 2) or (0 == end_ticks):
                    end_ticks = now_ticks
            else:
                break

    def startup(self):
        pass