# coding:utf-8
import os
import re
import sys
import json
import time
import random
import ffmpy3
import ffmpeg
import requests
import platform
import config_manager
import last_play_record_manager

import logger
from basic_media_player import basic_media_player


def _get_eps_dir(season_dir, tv_name, season):
    ep_dir = os.path.join(season_dir, '%s.S%02d' % (tv_name, season))
    if not os.path.exists(ep_dir):
        ep_dir = os.path.join(season_dir, '%d' % (season))
    return ep_dir


def _is_media_file_filter(path):
    if path.endswith('.mp4') or path.endswith('.mkv') or path.endswith(
            '.rmvb') or path.endswith('.rm'):
        return True
    return False


def _parse_play_list_item(str):
    str = str.replace('\r', '').replace('\n', '')
    splited = str.split(', ')
    return {
        'filename': splited[0],
        'start_time': splited[1],
        'end_time': splited[2]
    }


def _sort_by_filename(play_list_item):
    return play_list_item['filename']


def _get_play_list(ep_dir):
    play_list_path = os.path.join(ep_dir, 'playlist.txt')
    play_list = []
    if os.path.exists(play_list_path):
        with open(play_list_path, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                play_list.append(_parse_play_list_item(line))
    if len(play_list) == 0:
        media_list = list(filter(_is_media_file_filter, os.listdir(ep_dir)))
        for media_filename in media_list:
            play_list.append({
                'filename': media_filename,
                'start_time': '',
                'end_time': ''
            })
    play_list.sort(key=_sort_by_filename)
    return play_list


class tv_series_player(basic_media_player):
    def __init__(self, root, rtmp_url) -> None:
        super().__init__(root, rtmp_url)

    def _get_supportted_series(self):
        res = []
        path = os.path.join(self.root, 'supportted.dat')
        if not os.path.exists(path) or not os.path.isfile(path):
            for file_name in os.listdir(self.root):
                if os.path.isdir(os.path.join(self.root, file_name)):
                    res.append(file_name)
            return res
        with open(path, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                res.append(line.replace('\r', '').replace('\n', ''))
        return res

    def _select_tv_randomly(self, last_tv_name=''):
        paths = self._get_supportted_series()
        current_tv_name = ''
        while True:
            current_tv_name = random.sample(paths, k=1)[0]
            if current_tv_name != last_tv_name:
                break
        return current_tv_name

    def startup(self):

        # 获取上次播放的电视剧目录与集数
        name, start_season, start_ep, ss = last_play_record_manager.get_record(
        )

        while True:
            # 如果为空
            if name == '':
                # 随机选择一个电视剧
                name = self._select_tv_randomly(name)
                start_season = 1
                start_ep = 1

            # 拼接季目录路径
            season_dir = os.path.join(self.root, name)
            # 获取季数
            count_of_season = len(os.listdir(season_dir))
            logger.log_debug(f'count_of_season: {count_of_season}')

            for season in range(start_season, count_of_season + 1):
                # 拼接集目录
                ep_dir = _get_eps_dir(season_dir, name, season)
                logger.log_debug(f'ep_dir: {ep_dir}')

                play_list = _get_play_list(ep_dir)
                logger.log_debug(f'eps: {play_list}')

                count_of_ep = len(play_list)
                logger.log_debug(f'count_of_ep: {count_of_ep}')

                # 播放当季所有剧集
                for i in range(start_ep - 1, count_of_ep):
                    ep = i + 1
                    play_item = play_list[i]
                    media_path = os.path.join(ep_dir, play_item['filename'])
                    logger.log_debug(f'media_path: {media_path}')
                    last_play_record_manager.set_record(name, season, ep, ss)
                    play_option = {
                        'draw_text': ('S%02d E%02d' % (season, ep))
                        if config_manager.is_drawtext_enabled() else '',
                        'start_time':
                        play_item['start_time'],
                        'end_time':
                        play_item['end_time'],
                    }
                    self._play(media_path, play_option)
                    ss = '00:00:00'
                # 播完一季之后重置开始集数
                start_ep = 1
            # 播完所有季之后重置季数
            start_season = 1

            # 重新选取剧集
            name = self._select_tv_randomly(name)
        pass


if __name__ == '__main__':
    tv_series_player(r"Z:\chinese-tv",
                     f"rtmp://192.168.3.179/live/livestream").startup()
    pass