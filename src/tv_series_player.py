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

import logger
from basic_media_player import basic_media_player


class tv_series_player(basic_media_player):
    def __init__(self, root, rtmp_url) -> None:
        super().__init__(root, rtmp_url)

        if platform.system() == 'Windows':
            self.data_root_dir = r'.\data'
        else:
            self.data_root_dir = '/data'

        if not os.path.exists(self.data_root_dir):
            os.makedirs(self.data_root_dir)
        pass

    def _get_last_played_record_file_name(self):
        return 'last_played.json'

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

    def _get_last_play_record(self):
        line = ''
        path = os.path.join(self.data_root_dir,
                            self._get_last_played_record_file_name())
        if not os.path.exists(path) or not os.path.isfile(path):
            return ('', 0, 0)
        with open(path, mode='r', encoding='utf-8') as file:
            line = file.readline()
        if '' == line:
            return ('', 0, 0)
        obj = json.loads(line)
        return obj['name'], obj['season'], obj['ep']

    def _set_last_play_record(self, name, season, ep):
        if name == '' or 0 == season or 0 == ep:
            return
        path = os.path.join(self.data_root_dir,
                            self._get_last_played_record_file_name())
        with open(path, mode='w', encoding='utf-8') as file:
            file.write(json.dumps({'name': name, 'season': season, 'ep': ep}))
        pass

    def startup(self):

        # 获取上次播放的电视剧目录与集数
        name, season, ep = self._get_last_play_record()

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
            ep_dir = os.path.join(season_dir, str(season))
            eps = os.listdir(ep_dir)
            count_of_ep = len(eps)
            logger.log_debug(f'count_of_season: {count_of_season}')
            logger.log_debug(f'count_of_ep: {count_of_ep}')

            for s in range(season, count_of_season + 1):
                ep_file = eps[0]
                suffix = ep_file.split('.')[1]
                for e in range(ep, count_of_ep + 1):
                    media_path = os.path.join(self.root, name, str(s),
                                              '%02d.%s' % (e, suffix))
                    logger.log_debug(f'media_path: {media_path}')
                    self._set_last_play_record(name, s, e)
                    # self._play(media_path, '%s S%02d E%02d' % (name, s, e))
                    self._play(media_path)

            name = self._select_tv_randomly(name)
            season = 1
            ep = 1

        pass