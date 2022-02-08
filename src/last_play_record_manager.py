# coding:utf-8
import os
import json
import platform

if platform.system() == 'Windows':
    root_dir = r'.\data'
else:
    root_dir = '/data'


def _get_record_file_name():
    return 'last_played.json'


def _try_make_dir():
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)


def get_record():
    _try_make_dir()
    path = os.path.join(root_dir, _get_record_file_name())
    if not os.path.exists(path) or not os.path.isfile(path):
        return ('', 0, 0, '00:00:00')
    with open(path, mode='r', encoding='utf-8') as file:
        line = file.readline()
    if '' == line:
        return ('', 0, 0, '00:00:00')
    obj = json.loads(line)

    ep = ''
    ss = ''
    name = ''
    season = ''

    if 'ep' in obj:
        ep = obj['ep']
    if 'ss' in obj:
        ss = obj['ss']
    if 'name' in obj:
        name = obj['name']
    if 'season' in obj:
        season = obj['season']

    return name, season, ep, ss


def set_record(name, season, ep, ss='00:00:00'):
    _try_make_dir()
    path = os.path.join(root_dir, _get_record_file_name())
    if not os.path.exists(path) or not os.path.isfile(path):
        return
    if name == '' or 0 == season or 0 == ep:
        return
    with open(path, mode='w', encoding='utf-8') as file:
        file.write(
            json.dumps({
                'name': name,
                'season': season,
                'ep': ep,
                'ss': ss
            }))
    pass


def get_start_time():
    _try_make_dir()
    path = os.path.join(root_dir, _get_record_file_name())
    if not os.path.exists(path) or not os.path.isfile(path):
        return ('00:00:00')
    with open(path, mode='r', encoding='utf-8') as file:
        line = file.readline()
    if '' == line:
        return ('00:00:00')
    obj = json.loads(line)

    ss = '00:00:00'

    if 'ss' in obj:
        ss = obj['ss']

    if '' == ss:
        ss = '00:00:00'

    return ss


def set_start_time(val):
    _try_make_dir()
    path = os.path.join(root_dir, _get_record_file_name())
    if not os.path.exists(path) or not os.path.isfile(path):
        return
    line = ''
    with open(path, mode='r', encoding='utf-8') as file:
        line = file.readline()
    if '' == line:
        return
    obj = json.loads(line)
    obj['ss'] = val
    with open(path, mode='w', encoding='utf-8') as file:
        file.write(json.dumps(obj))