# -*- coding: UTF-8 -*-
import os
import time
import platform

if platform.system() == 'Windows':
    root_dir = r'.\logs'
else:
    root_dir = '/logs'


def _make_log_file_name():
    date_string = time.strftime("%Y-%m-%d", time.localtime())
    return f'{date_string}.log'


def _make_log_content(level, content):
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f'{local_time} [{level}] {content}'


def _log_to_file(content):
    if platform.system() == 'Linux':
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        path = os.path.join(root_dir, _make_log_file_name())
        with open(path, mode='a', encoding='utf-8') as file:
            file.write(f'{content}\n')
    else:
        print(content)


def log_debug(content):
    _log_to_file(_make_log_content('DEBUG', content))


def log_error(content):
    _log_to_file(_make_log_content('ERROR', content))


def startup():
    pass