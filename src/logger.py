# -*- coding: UTF-8 -*-
import os
import time
import platform

if platform.system() == 'Windows':
    root_dir = r'.\logs'
else:
    root_dir = '/logs'


def _make_log_file_name(prefix=''):
    date_string = time.strftime("%Y-%m-%d", time.localtime())
    return f'{prefix}{date_string}.log'


def _make_log_content(level, content):
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return f'{local_time} [{level}] {content}'


def _log_to_file(content, prefix=''):
    if platform.system() == 'Linux':
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
        path = os.path.join(root_dir, _make_log_file_name(prefix))
        with open(path, mode='a', encoding='utf-8') as file:
            file.write(f'{content}\n')
    else:
        print(content)


def log_debug(content, prefix=''):
    _log_to_file(_make_log_content('DEBUG', content), prefix)


def log_error(content, prefix=''):
    _log_to_file(_make_log_content('ERROR', content), prefix)


def startup():
    pass