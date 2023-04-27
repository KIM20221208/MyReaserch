import time
import json
import csv
import os
import sys

import Util

l_err = list()  # 用来装报错的用户，及报错原因
timeStart = time.time()  # 用来计算下列循环所用事件，开始
path = "C:/Users/JinCh/PycharmProjects/pythonProject/Steam/games/data_ver4/"
# 打开获取到的TOP100游戏文件
with open(f'TOP 100 FPS.csv', encoding='utf-8', mode='r') as f:
    csvReader = csv.reader(f)
    # Passing the cav_reader object to list() to get a list of lists
    gameList = list(csvReader)

for g in gameList:
    game = Util.Game(g[0], g[1], path)  # 声明Util.Game对象
    game.getJsonFileNum()
    os.chdir(game.path)

    for fileNum in range(1, game.jsonFileNum + 1):
        print("Now crawling \"{}\"".format(game.title), fileNum, "/", game.jsonFileNum, "th file")
        # 检查第fileNum个json文件是否已经爬完
        if os.path.exists(f"{game.title}_{fileNum}Achievements.csv"):
            print(f"\"{game.title}_{fileNum}Achievements.csv\" exist, crawling next one.")
            continue
        else:
            with open(f"{game.title}_{fileNum}reviews.json", mode='r') as f:
                l_Reviews = json.load(f)
                f.close()

            # 声明一些在下面的for循环中使用的变量
            l_data = list()  # 用来装用户数据
            x = int(1)  # 用来确认循环次数
            for review in l_Reviews:
                # 声明Util.User对象
                try:
                    user = Util.User(review["steamid"], review["hours"], review["last_tow_weeks"],
                                     review["last_played"])
                    d_UserAchievements = user.getAchievements(game.appId, game.d_NormalizedGlobalAchievements)
                    # k是成就名，v列表中保存的依次是：score, unlockDate, unlockYear, week, status
                    for k, v in d_UserAchievements.items():
                        steamId, hours, lastTwoWeeks, lasPlayed, lastPlayedYear, nationality, level, badges, games, \
                        friends, groups, screenshots, recommended, ifDisorder = user.getMember()
                        l_data.append([steamId, hours, lastTwoWeeks, ifDisorder, lasPlayed, lastPlayedYear, nationality,
                                       level, badges, games, friends, groups, screenshots, recommended,
                                       k, v[0], v[1], v[2], v[3], v[4]])
                    tmpTimeEnd = time.time()
                    print(x, "/ {}, steamId: {}, current time cost:".format(len(l_Reviews), user.steamId),
                          Util.timeParser(tmpTimeEnd - timeStart))
                    x += 1  # 每次循环结束时++
                    user.closeProfileResp()  # 关闭上述用户的resp
                except:
                    print(review["steamid"], "crawling failed.")
                    l_err.append([game.title, fileNum, review["steamid"], sys.exc_info()])

            with open(f"{game.title}_{fileNum}Achievements.csv", mode='w', encoding='UTF-8', newline='') as f:
                csvWriter = csv.writer(f)
                csvWriter.writerow(
                    ["Steam ID", "Hours", "Last Two Weeks", "If disorder", "Last Played", "Last Played Year", "Nation",
                     "Level", "Badges", "Games", "Friends", "Groups", "ScreenShots", "Reviews", "Achievement",
                     "Score", "Unlock date", "Unlock Year", "Week", "Status"])
                for l in l_data:
                    csvWriter.writerow(l)
                f.close()

    game.hoursAdjust()

timeEnd = time.time()  # 用来计算下列循环所用事件，结束
#  打印错误列表
for l in l_err:
    print(l)
print("program completed! cost:", Util.timeParser(timeEnd - timeStart))
