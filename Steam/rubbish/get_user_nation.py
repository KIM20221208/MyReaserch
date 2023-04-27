"""获取用户的国籍，成就，成就解锁时间，成就标准化分数"""
from imports import *
# 调用成就标准化模块
import data_normalization

# steam用户id列表
steamId_list = ["76561199158211742", "76561198081140767"]
appId = 578080
# 调用成就标准化模块
global_achievement_normalized_dic = data_normalization.normalization(appId)

for steamId in steamId_list:
    # 取得用户国籍
    personal_url = f"https://steamcommunity.com/profiles/{steamId}/"
    personal_resp = requests.get(personal_url)
    
    personal_page = BeautifulSoup(personal_resp.text, "html.parser")
    div = personal_page.find("div", class_="header_real_name ellipsis")
    visible = div.text.split('\n')
    # 如果用户国籍可见，则取得，否则定义为不可见
    if len(visible) == 5:
        nation = visible[-1].strip('\t')
    else:
        nation = "unVisible"

    # 取得用户成就和解锁时间
    achievement_url = f"https://steamcommunity.com/profiles/{steamId}/stats/{appId}/?tab=achievements"

    achievement_resp = requests.get(achievement_url)
    if not achievement_resp:
        continue
    else:
        achievement_page = BeautifulSoup(achievement_resp.text, "html.parser")
        divs = achievement_page.find_all("div", class_="achieveRow")

        if divs:
            for div in divs:
                achievement_title = div.find("h3", class_="ellipsis").text.strip()
                score = global_achievement_normalized_dic[achievement_title]
                unlock_time = div.find("div", class_="achieveUnlockTime")
                if unlock_time is None:
                    unlock_time = "Locked"
                # 修改时间显示
                else:
                    unlock_time = unlock_time.text.strip().strip("Unlocked ").split("@")
                    unlock_time_format = unlock_time[0].strip().split(",")
                    # print(unlock_time_format)
                    if len(unlock_time_format) == 2:
                        unlock_time = unlock_time[1].strip() + ' ' + unlock_time_format[0] + unlock_time_format[1]
                    else:
                        today = datetime.datetime.today()
                        # 如果是本年度解锁的评论，则需要加上年份
                        unlock_time = unlock_time[1] + ' ' + unlock_time_format[0] + ' ' + str(today.year)  # 需要把int型年份转化为str

                print(nation, achievement_title, unlock_time, score)

    personal_resp.close()
    achievement_resp.close()
