# coding:utf-8
import time
import json
import logger
import bilibili_http_api


def _log_debug(content):
    logger.log_debug(content=content, prefix='live_checker-')


def _log_error(content):
    logger.log_error(content=content, prefix='live_checker-')


# if __name__ == "__main__":
def startup():
    while True:
        try:
            response = bilibili_http_api.start_live()
            message = response['message']
            if message != '重复开播':
                _log_debug(f'{message}')
        except Exception as ex:
            _log_error(f'{ex}')

        time.sleep(5)