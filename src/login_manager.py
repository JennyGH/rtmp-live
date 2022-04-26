# coding:utf-8
import os
import json
import logger
import platform

if platform.system() == 'Windows':
    root_dir = r'.\data'
else:
    root_dir = '/data'


def get_csrf():
    try:
        path = os.path.join(root_dir, 'login_status.json')

        if not os.path.exists(path):
            return ''

        json_string = ''
        with open(path, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'

        obj = json.loads(json_string)

        if 'csrf' not in obj:
            logger.log_error('No `csrf` in login_status.json')
            return ''

        csrf = obj['csrf']

        logger.log_debug(f'csrf: {csrf}')

        return csrf

    except Exception as ex:
        logger.log_error(f'Unable to get csrf, {ex}')
        return ''


def get_csrf_token():
    try:
        path = os.path.join(root_dir, 'login_status.json')

        if not os.path.exists(path):
            return ''

        json_string = ''
        with open(path, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'

        obj = json.loads(json_string)

        if 'csrf_token' not in obj:
            logger.log_error('No `csrf_token` in login_status.json')
            return ''

        csrf_token = obj['csrf_token']

        # logger.log_debug(f'csrf_token: {csrf_token}')

        return csrf_token

    except Exception as ex:
        logger.log_error(f'Unable to get csrf_token, {ex}')
        return ''


def get_cookies():
    try:
        path = os.path.join(root_dir, 'login_status.json')

        if not os.path.exists(path):
            return ''

        json_string = ''
        with open(path, mode='r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                json_string += f'{line}\n'

        obj = json.loads(json_string)

        if 'cookies' not in obj:
            logger.log_error('No `cookies` in login_status.json')
            return ''

        cookies = obj['cookies']

        # logger.log_debug(f'cookies: {cookies}')

        return cookies

    except Exception as ex:
        logger.log_error(f'Unable to get cookies, {ex}')
        return ''