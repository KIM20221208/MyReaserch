# 1. 定位到具体游戏
# 2. 提取具体游戏的子页面的链接地址
# 3. 请求子页面的链接，拿到想要的数据：1.评价相关 2. 标签 3.留言
import requests
import re
from lxml import etree
import csv


def get_resp(appID, game_name):
# 拿到游戏具体游戏的子页面的链接
# 这部分有提升空间，可以设置变量来定位不同游戏，但是app后面的数字的规律是什么?
url = f"https://store.steampowered.com/app/242760/The_Forest/"
resp = requests.get(url)
# print(resp.text) #  成功获取

# 写入数据
f = open("mainData.csv", mode="w", newline='')
csvwriter = csv.writer(f)
csvwriter.writerow(["release_date", "description", "total_reviews"])
# 评价相关：xpath解析
html = etree.HTML(resp.text)
# print(html)

release_date = html.xpath('//*[@id="appHeaderGridContainer"]/div[6]/text()')
description = html.xpath('//*[@id="appReviewsAll_responsive"]/div[2]/span[1]/text()')
total_reviews = html.xpath('//*[@id="appReviewsAll_responsive"]/div[2]/span[2]/text()')
csvwriter.writerow([release_date, description, total_reviews])


# 标签：re解析
obj2 = re.compile(r'<a href="https://store.steampowered.com/tags/en/(?P<tag>.*?)/?snr=1_5_9__409"', re.S)
result = obj2.finditer(resp.text)
csvwriter.writerow(["tag"])

for it in result:
    tag = it.group("tag").strip("/?")
    # print(tag)
    csvwriter.writerow([tag])

f.close()
print("Over!")
resp.close()
