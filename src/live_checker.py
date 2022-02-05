# coding:utf-8
import json
from urllib import response
import logger
import requests
import login_manager
import bilibili_http_api
from time import sleep


# if __name__ == "__main__":
def startup():
    while True:
        try:
            response = bilibili_http_api.start_live()
            message = response['message']
            if message != '重复开播':
                logger.log_debug(f'{message}')
        except Exception as ex:
            logger.log_error(f'{ex}')

        sleep(5)