"""按照 TOP SELLERS 获得前100名的FPS游戏排名"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

# 计数器
i = 1

# 打开网页，默认语言为英文
options = webdriver.ChromeOptions()
options.add_argument('lang=en_US')
web = webdriver.Chrome(options=options)
url = "https://store.steampowered.com/tags/en/FPS/?flavor=contenthub_topsellers"
web.get(url)
time.sleep(2)

for i in range(10):
    # 点击 'show more' 按钮
    button = web.find_element(by=By.CLASS_NAME, value='saleitembrowser_ShowContentsContainer_3IRkb')
    button.click()
    print(f"clicked {i + 1} times.")
    time.sleep(2)

game_list = web.find_elements(by=By.CLASS_NAME, value='salepreviewwidgets_TitleCtn_1F4bc')
Top100List = list()
for l in game_list:
    game_title = l.find_element(by=By.CLASS_NAME, value='salepreviewwidgets_StoreSaleWidgetTitle_3jI46').text
    game_url = l.find_element(by=By.XPATH, value='./a').get_attribute('href')
    appID = game_url.split('/')[4]
    Top100List.append([game_title, appID, game_url])
    i += 1

with open("TOP 100 FPS.csv", mode='w', encoding='utf-8', newline='') as f:
    csvWriter = csv.writer(f)
    csvWriter.writerow(["Game Title", "appID", "Game URL"])
    for l in Top100List:
        csvWriter.writerow(l)
    f.close()

web.close()
