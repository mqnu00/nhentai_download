import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from Downloader import Downloader
from tqdm import tqdm
from subprocess import call


# 计算过，由于为了减轻服务器压力和 cloudflare 的拦截使用了 time.sleep(1)，下载100页的漫画大概需要8分多钟
# 如果使用 IDM 下载，40 页需要 1 分 20 秒 左右，而且获取到图片源地址后似乎不会被 cloudflare 拦截


class NhentaiDownloader():

    downloader = Downloader(None)
    url = None

    def __init__(self, url, file_path=None, file_name=None, idm_path=None, headers=None, cookies=None):
        self.downloader = Downloader(
            url,
            file_path,
            file_name,
            idm_path,
            headers,
            cookies
        )
        self.url = url

    # 获取漫画的信息
    def comic_info(self):
        resp = self.downloader.url_get()
        if resp:
            soup = BeautifulSoup(resp.content, 'html.parser')
            comic_name = soup.find_all('span', class_='pretty')[-1].text
            tot_page = soup.find_all('span', class_='name')[-1].text
            gallery_id = soup.find_all('h3', id='gallery_id')[-1].text
            return {
                "comic_name": comic_name,
                "tot_page": tot_page,
                "gallery_id": gallery_id,
            }

    def download(self):
        comic_dict = self.comic_info()
        tot_page = comic_dict["tot_page"]
        comic_name = re.sub(r'[\\/:*?"<>|]', '', comic_dict["comic_name"])
        gallery_id = comic_dict["gallery_id"]
        print(self.downloader.file_path)
        self.downloader.file_path = self.downloader.file_path + '/' + comic_name + gallery_id + '/'
        self.downloader.create_folder()
        print("一共" + str(tot_page) + "页")
        for i in range(1, int(tot_page) + 1):
            self.downloader.url = self.url + str(i) + '/'
            self.downloader.file_name = str(i) + '.jpg'
            pic_page = self.downloader.url_get()
            soup = BeautifulSoup(pic_page.content, "html.parser")
            pic_url = soup.find_all('img')[-1]['src']
            self.downloader.url = pic_url
            # download_gui(pic_url, file_path, str(i) + '.jpg')
            self.downloader.idm_download()


if __name__ == "__main__":
    test = NhentaiDownloader(
        url="",
        file_path="",
        idm_path="",
        headers=None,
        cookies=None,
    )
    test.download()