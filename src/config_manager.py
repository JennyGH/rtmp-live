# coding:utf-8
import os
import re
import sys
import json
import time
import platform

import logger

if platform.system() == 'Windows':
    root_dir = r'.\data'
else:
    root_dir = '/data'


def _get_config_file_name():
    return os.path.join(root_dir, 'config.json')


def get_live_time_range():
    try:
        path = _get_config_file_name()
        if not os.path.exists(path):
            return (0, 0)
        json_string = ''
        with open(path, mode='rt', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'
        obj = json.loads(json_string)
        if 'live_time_range' not in obj:
            return (0, 0)
        live_time_range = obj['live_time_range']
        if 'begin' not in live_time_range or 'end' not in live_time_range:
            return (0, 0)

        return (live_time_range['begin'], live_time_range['end'])
    except:
        return (0, 0)


def set_live_time_range(begin, end):
    path = _get_config_file_name()
    json_string = json.dumps(
        {'live_time_range': {
            'begin': begin,
            'end': end,
        }})
    with open(path, mode='w', encoding='utf-8') as file:
        file.write(json_string)
    pass


def is_in_live_time():
    live_time_begin, live_time_end = get_live_time_range()
    hour = time.localtime().tm_hour
    return True


def get_live_src():
    try:
        path = _get_config_file_name()
        if not os.path.exists(path):
            return ''
        json_string = ''
        with open(path, mode='rt', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'
        obj = json.loads(json_string)
        if 'live_src' not in obj:
            return ''
        live_src = obj['live_src']
        return live_src
    except Exception as ex:
        logger.log_error(f'Unable to get live src, {ex}')
        return ''


def get_live_url():
    try:
        path = _get_config_file_name()
        if not os.path.exists(path):
            return ''
        json_string = ''
        with open(path, mode='rt', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'
        obj = json.loads(json_string)
        if 'live_url' not in obj:
            return ''
        live_url = obj['live_url']
        return live_url
    except Exception as ex:
        logger.log_error(f'Unable to get live url, {ex}')
        return ''


def is_drawtext_enabled():
    try:
        path = _get_config_file_name()
        if not os.path.exists(path):
            return False
        json_string = ''
        with open(path, mode='rt', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'
        obj = json.loads(json_string)
        if 'drawtext' not in obj:
            return False
        drawtext = obj['drawtext']
        return drawtext
    except Exception as ex:
        logger.log_error(f'Unable to get enable drawtext, {ex}')
        return False
