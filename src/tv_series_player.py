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
import last_play_record_manager

import logger
from basic_media_player import basic_media_player


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

    def _is_media_file_filter(path):
        if path.endswith('.mp4') or path.endswith('.mkv') or path.endswith(
                '.rmvb') or path.endswith('.rm'):
            return True
        return False

    def startup(self):

        # 获取上次播放的电视剧目录与集数
        name, season, ep, ss = last_play_record_manager.get_record()

        while True:
            # 如果为空
            if name == '':
                # 随机选择一个电视剧
                name = self._select_tv_randomly(name)
                season = 1
                ep = 1

            # 获取总集数
            season_dir = os.path.join(self.root, name)
            count_of_season = len(os.listdir(season_dir))
            ep_dir = os.path.join(season_dir, '%s.S%02d' % (name, season))
            if not os.path.exists(ep_dir):
                ep_dir = os.path.join(season_dir, '%d' % (season))
            eps = list(
                filter(tv_series_player._is_media_file_filter,
                       os.listdir(ep_dir)))
            logger.log_debug(f'eps: {eps}')
            count_of_ep = len(eps)
            logger.log_debug(f'count_of_season: {count_of_season}')
            logger.log_debug(f'count_of_ep: {count_of_ep}')

            for s in range(season, count_of_season + 1):
                ep_file = eps[0]
                suffix = ep_file.split('.')[1]
                for e in range(ep, count_of_ep + 1):
                    season_dir = os.path.join(self.root, name,
                                              '%s.S%02d' % (name, s))
                    if not os.path.exists(season_dir):
                        season_dir = os.path.join(self.root, name, '%d' % s)
                    media_path = os.path.join(season_dir,
                                              '%02d.%s' % (e, suffix))
                    logger.log_debug(f'media_path: {media_path}')
                    last_play_record_manager.set_record(name, s, e, ss)
                    # self._play(media_path, '%s S%02d E%02d' % (name, s, e))
                    self._play(media_path)
                    ss = '00:00:00'

            name = self._select_tv_randomly(name)
            season = 1
            ep = 1

        pass