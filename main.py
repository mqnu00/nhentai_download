import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# 计算过，由于为了减轻服务器压力和 cloudflare 的拦截使用了 time.sleep(1)，下载100页的漫画大概需要8分多钟

# 下载的网址
url = ""
# 保存的地址
save_path = ""

# headers 和 cookies 要自己手动填写，不然可能绕不过cloudflare

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
                  "Safari/537.36 Edg/114.0.1823.67",
}

cookies = {
    "cf_clearance": "fnrInzgvGLTWdIebQ5kO.pTYM3OWPj1VkM7_tfPv9Fo-1688376149-0-250",
    "csrftoken": "NPqEkGxttsYdBxcKXYuWutOh8CChqXFZ61Gyul8wEz92V9QpFGMOZ6GMi7RsgLk9",
}


# 建立文件夹
def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)


# 封装 requests.get
def url_get(target_url):
    cnt = 0
    while cnt < 3:
        try:
            res = requests.get(
                target_url,
                headers=headers,
                cookies=cookies,
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
def url_get_stream(target_url):
    cnt = 0
    while cnt < 3:
        try:
            response = requests.get(
                target_url,
                stream=True,
                headers=headers,
                cookies=cookies,
                allow_redirects=False,
                timeout=10
            )
            time.sleep(1)
            return response
        except Exception:
            print("超时，" + f"第{cnt + 1}次重连")
            cnt = cnt + 1


# 进度条下载
def download_gui(download_url, file_path, file_name):
    try:
        response = url_get_stream(download_url)
    except Exception:
        print("不知道出了什么问题")
    # 获取文件大小
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    # 每次下载的字长
    block_size = 1024

    # 获取以前下载的大小，断点续传
    if os.path.exists(file_path + '/' + file_name):
        first_byte = os.path.getsize(file_path + '/' + file_name)
    else:
        first_byte = 0
    if first_byte >= total_size_in_bytes:
        print(file_name + "已下载完成")
        return
    else:
        first_byte = 0

    # 显示下载进度条
    progress_bar = tqdm(
        total=total_size_in_bytes,
        initial=first_byte,
        unit='B',
        unit_scale=True,
        desc=file_path + '/' + file_name
    )
    # 数据下载到文件
    with open(file_path + '/' + file_name, 'wb') as file:
        for data in response.iter_content(block_size):
            if data:
                progress_bar.update(len(data))
                file.write(data)
    return


# 获取漫画的信息
def comic_info():
    resp = url_get(url)
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


# 下载
def download():
    comic_dict = comic_info()
    tot_page = comic_dict["tot_page"]
    comic_name = re.sub(r'[\\/:*?"<>|]', '', comic_dict["comic_name"])
    gallery_id = comic_dict["gallery_id"]
    file_path = save_path + '/' + comic_name + gallery_id + '/'
    create_folder(file_path)
    print("一共" + str(tot_page) + "页")
    for i in range(1, int(tot_page) + 1):
        now = url + str(i) + '/'
        pic_page = url_get(now)
        soup = BeautifulSoup(pic_page.content, "html.parser")
        pic_url = soup.find_all('img')[-1]['src']
        download_gui(pic_url, file_path, str(i) + '.jpg')


if __name__ == "__main__":
    download()
