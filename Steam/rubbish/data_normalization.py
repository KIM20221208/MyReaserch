"""此模块用来得到成就名称对应min_max标准化的dic"""
from imports import *


# 1. 首先需要取得成就的全球百分比数据
def get_global_achievement(appId):
    global_achievement_url = f"https://steamcommunity.com/stats/{appId}/achievements/"
    global_achievement_resp = requests.get(global_achievement_url)

    global_achievement_page = BeautifulSoup(global_achievement_resp.text, "html.parser")
    divs = global_achievement_page.find_all("div", class_="achieveRow")

    lists = list()

    for div in divs:
        achievement_title = div.find("h3").text.strip()
        achievement_percent = div.find("div", class_="achievePercent").text
        # print(achievement_title, achievement_percent)
        lists.append([achievement_title, achievement_percent])

    # print(lists)
    global_achievement_resp.close()

    return lists


# 数据标准化
def min_max_normalization(list):
    # 2-1. 进行 1 - ratio 的操作
    for l in list:
        l[1] = 1 - (float(l[1].strip("%")) * 0.01)
    # 2-2. 选取最值，均在列表的两端
    min = list[0][1]
    max = list[-1][1]
    # 3. 最后进行标准化计算（min_max_normalization），但数据会变成[0，1]区间
    for l in list:
        l[1] = round((l[1] - min) / (max - min), 2)  # 保留小数点后2位数

    dic = dict()
    # 匹配成就名和score
    for l in list:
        dic[l[0]] = l[1]

    dic["No data"] = "No data"

    return dic


# 输入游戏编号，得到标准化后的成就字典
def normalization(appId):
    # 调用函数
    global_achievement_list = get_global_achievement(appId)
    if len(global_achievement_list) != 0:
        global_achievement_dic = min_max_normalization(global_achievement_list)
        # for k, v in global_achievement_dic.items():
            # print(k, v)
    else:
        global_achievement_dic = {"No Data": "No Data"}

    return global_achievement_dic
