import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from subprocess import call


class Downloader():
    url = None
    cookies = None
    headers = None
    file_path = None
    file_name = None
    idm_path = None
    idm_exe = "IDMan.exe"

    def __init__(self, url, file_path=None, file_name=None, idm_path=None, headers=None, cookies=None):
        self.url = url
        self.cookies = cookies
        self.headers = headers
        self.file_path = file_path
        self.file_name = file_name
        self.idm_path = idm_path

    # 建立文件夹
    def create_folder(self):
        print(self.file_path)
        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)

    # 封装 requests.get
    def url_get(self):
        cnt = 0
        while cnt < 3:
            try:
                res = requests.get(
                    self.url,
                    headers=self.headers,
                    cookies=self.cookies,
                    allow_redirects=False,
                    timeout=10
                )
                time.sleep(1)
                return res
            except Exception:
                print("超时第" + str(cnt + 1) + "次重连")
                cnt = cnt + 1
        return

    # requests.get stream
    def url_get_stream(self):
        cnt = 0
        while cnt < 3:
            try:
                response = requests.get(
                    self.url,
                    stream=True,
                    headers=self.headers,
                    cookies=self.cookies,
                    allow_redirects=False,
                    timeout=10
                )
                time.sleep(1)
                return response
            except Exception:
                print("超时，" + f"第{cnt + 1}次重连")
                cnt = cnt + 1

    # 进度条下载
    def download_gui(self):
        try:
            response = self.url_get_stream()
        except Exception:
            print("不知道出了什么问题")
        # 获取文件大小
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        # 每次下载的字长
        block_size = 1024

        # 获取以前下载的大小，断点续传
        if os.path.exists(self.file_path + '/' + self.file_name):
            first_byte = os.path.getsize(self.file_path + '/' + self.file_name)
        else:
            first_byte = 0
        if first_byte >= total_size_in_bytes:
            print(self.file_name + "已下载完成")
            return
        else:
            first_byte = 0

        # 显示下载进度条
        progress_bar = tqdm(
            total=total_size_in_bytes,
            initial=first_byte,
            unit='B',
            unit_scale=True,
            desc=self.file_path + '/' + self.file_name
        )
        # 数据下载到文件
        with open(self.file_path + '/' + self.file_name, 'wb') as file:
            for data in response.iter_content(block_size):
                if data:
                    progress_bar.update(len(data))
                    file.write(data)
        return

    def idm_download(self):
        # os.chdir(idm_path)
        # command = ' '.join([idm_exe, '/d', download_url, '/p', file_path, '/f', file_name, '/n'])
        # os.system(command)
        # 下载文件链接（注意是这个列表）
        urlList = [self.url]
        # 将下载链接全部加入到下载列表，之后再进行下载。
        for ul in urlList:
            call([self.idm_path + '/' + self.idm_exe, '/d', ul, '/p', self.file_path, '/f', self.file_name, '/n', '/a'])
        print("添加到下载列表完成")
        call([self.idm_path + '/' + self.idm_exe, '/s'])


if __name__ == "__main__":
    test = Downloader(
        url=None
    )
