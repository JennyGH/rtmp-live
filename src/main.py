# coding:utf-8
from mimetypes import init
import os
import re
import sys
import json
import time
import random
import ffmpy3
import ffmpeg
import requests
import threading

# Custom modules
import logger
import live_checker
import login_manager
import config_manager
import message_manager
import bilibili_http_api
from tv_series_player import tv_series_player


def log_debug(content):
    # print(f'[DEBUG] {content}')
    logger.log_debug(content=content)


def log_error(content):
    # print(f'[ERROR] {content}')
    logger.log_error(content=content)


def _get_movie_path_randomly(root_path, old_movie_name):
    paths = []
    for file_name in os.listdir(root_path):
        path = os.path.join(root_path, file_name)
        if path.endswith('.mp4'):
            paths.append(path)
    selected_path = ''
    while True:
        selected_path = random.sample(paths, k=1)[0]
        selected_file_name = os.path.basename(selected_path)
        current_movie_name = _get_movie_name_from_file_name(selected_file_name)
        if current_movie_name != old_movie_name:
            break
    return selected_path


def _get_movie_name_from_file_name(file_name):
    found = re.findall(r'[\[SHANA\]]*\[(.*)\].*', file_name, re.IGNORECASE)
    if None == found or len(found) == 0:
        return ''
    return found[0]


def _is_a_valid_media_file(path):
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


def _try_play(ff):
    try:
        ff.run()
        return True
    except:
        return False


def _play_movie(in_path, out_path):
    log_debug(f'Play {in_path}')
    start_ticks = 0
    end_ticks = 0
    while True:
        during_seconds = end_ticks - start_ticks
        m, s = divmod(during_seconds, 60)
        h, m = divmod(m, 60)
        ss = "-ss " + ("%02d:%02d:%02d" % (h, m, s))
        ff = ffmpy3.FFmpeg(global_options=["-re"],
                           inputs={in_path: f"{ss}"},
                           outputs={out_path: "-c copy -b:v 3000k -f flv"})
        log_debug(ff.cmd)

        # 如果 开始时间 和 结束时间 相等，说明是从头开始播放的，记录开始时间
        if end_ticks == start_ticks:
            start_ticks = time.time()
        success = _try_play(ff)
        now_ticks = time.time()
        # 如果播放失败了
        if not success:
            end_ticks = now_ticks
        else:
            break


def _startup_movie_player(root_dir, rtmp_url):
    # 上一次选取的电影名称
    old_movie_name = ''

    # 不停地轮播
    while True:
        # 随机地选择电影，返回电影文件路径
        path = _get_movie_path_randomly(root_dir, old_movie_name)

        # 检查是否有效的媒体文件
        if not _is_a_valid_media_file(path):
            # 跳过无效的媒体文件
            continue

        # 从路径中提取出当前的电影名称
        new_movie_name = _get_movie_name_from_file_name(os.path.basename(path))

        # 更新上一次选取的电影名称
        old_movie_name = new_movie_name

        # 查询B站官方是否已存在该电影会员专享版
        exists = False  #_check_if_movie_exists_in_official_site(new_movie_name)

        # 如果不存在，直接播放
        if not exists:
            _play_movie(path, rtmp_url)
            pass
        # 否则，在下一循环中重新选择
        else:
            continue


def _startup_tv_player(root_dir, rtmp_url):

    # 获取最后一次播放的电视剧名称和集数

    pass


def _startup_live_checker():
    live_checker.startup()


def _startup_message_manager():
    message_manager.startup()


if __name__ == "__main__":

    live_src = config_manager.get_live_src()
    live_url = config_manager.get_live_url()

    logger.log_error(f'live_src: {live_src}')
    logger.log_error(f'live_url: {live_url}')

    if bilibili_http_api.is_bilibili_host(live_url):
        # 启动开播检测服务，在直播被掐断的时候可以自动重新开播
        live_checker_thread = threading.Thread(target=_startup_live_checker)
        live_checker_thread.start()
        live_checker_thread.join(timeout=3)

        # 启动弹幕服务
        message_thread = threading.Thread(target=_startup_message_manager)
        message_thread.start()
        message_thread.join(timeout=3)

    player = tv_series_player(live_src, live_url)
    player.startup()

    # # 启动轮播服务
    # _startup_movie_player(root_dir=live_src, rtmp_url=live_url)