import csv
import datetime
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

# 英文月份转换数字用字典
monthTransDic = {
    "Jan": "1",
    "Feb": "2",
    "Mar": "3",
    "Apr": "4",
    "May": "5",
    "Jun": "6",
    "Jul": "7",
    "Aug": "8",
    "Sep": "9",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}


# 拿到秒数， 返回hour, minute, second
def timeParser(sec):
    hour = int(sec / 3600)
    minute = int((sec - hour * 3600) / 60)
    second = int(sec - (hour * 60 + minute) * 60)
    hourMinuteSecond = str(hour) + ':' + str(minute) + ':' + str(second)
    return hourMinuteSecond


# 将12小时表示的时间转换为24小时，
def timeTrans(clock_12):
    """ clock_12 = "XX:XXam/pm"
        clock_24 = "XX:XX" """
    if clock_12.find("pm") != -1:
        clock_24 = str(int(clock_12.split(':')[0]) + 12) + ':' + clock_12.split(':')[1].strip("pm")
    else:
        clock_24 = clock_12.strip("am")

    return clock_24


class User:
    # 初始化
    def __init__(self, steamId, hours, lastTwoWeeks, lastPlayed):
        self.steamId = steamId
        self.hours = round(float(hours) / 60, 2)
        self.lastTwoWeeks = round(float(lastTwoWeeks) / 60, 2)
        self.lasPlayed, self.lastPlayedYear = self.newLastPlayed(lastPlayed)
        self.profileURL = "https://steamcommunity.com/profiles/" + steamId
        self.profileResp, self.profilePage = self.getProfilePage()
        self.nationality = self.getNationality()
        self.level = self.getLevel()
        self.badges, self.games, self.friends, self.groups, self.screenshots, self.recommended = self.getRightCol
        self.ifDisorder = self.checkIfDisorder()

    # 返回类的成员变量
    def getMember(self):
        return self.steamId, self.hours, self.lastTwoWeeks, self.lasPlayed, self.lastPlayedYear, self.nationality, \
               self.level, self.badges, self.games, self.friends, self.groups, self.screenshots, self.recommended, \
               self.ifDisorder

    # lastPlayed的"d-m-y"日期格式改为"y/m/d"
    @staticmethod
    def newLastPlayed(lastPlayed):
        l_date = lastPlayed.split('-')
        # Last Played Year
        year = "20" + l_date[-1]
        month = l_date[1]
        day = l_date[0]
        newLastPlayed = year + '/' + month + '/' + day
        return newLastPlayed, year

    # 按最近两周的游戏时间初步判断是否为游戏障碍用户
    def checkIfDisorder(self):
        if self.lastTwoWeeks >= 70.98:
            ifDisorder = 2
        elif 42.7 <= self.lastTwoWeeks:
            ifDisorder = 1
        elif self.lastTwoWeeks < 42.7:
            ifDisorder = 0
        else:
            ifDisorder = "No data"
        return ifDisorder

    # nationality
    def getNationality(self):
        """
        :param: BEAUTIFULSOUP.html.parser后的树状体
        :return: User nationality or "unVisible"
        """
        nationalityDiv = self.profilePage.find("div", class_="header_real_name ellipsis")
        # 检查国籍是否可见，且正确设置
        if nationalityDiv and len(nationalityDiv.text.strip().split('\n')) >= 2:
            nationality = nationalityDiv.text.strip().split('\n')[-1].strip('\t')
        else:
            nationality = "No Data"
        return nationality

    # level
    def getLevel(self):
        """
        :param: parsed profile Responsibility
        :return: User level or "No Data"
        """
        levelSpan = self.profilePage.find("span", class_="friendPlayerLevelNum")
        if levelSpan:
            level = levelSpan.text
        else:
            level = "No Data"
        return level

    # from right column get: badges, games, friends, groups, screenshots, recommended
    @property
    def getRightCol(self):
        d_rightColList = {
            "badges": "NO Data",
            "games": "NO Data",
            "friends": "NO Data",
            "groups": "NO Data",
            "screenshots": "NO Data",
            "recommended": "NO Data"
        }
        l_wantedData = ["badges", "games", "friends", "groups", "screenshots", "recommended"]
        # 用re的正则路径拿到可以定位右侧栏具体信息的profileURL（有些人的不是./profile/而是./id/）
        obj = re.compile(r"class=\"persona_level_btn\" href=\"(?P<href>.*?)/badges", re.S)
        if self.level != "No Data":  # 如果 level的tag存在
            try:
                # 开始从level的tag中获取新的用户URL
                newProfileURL = obj.finditer(self.profileResp.text).__next__().group("href")
            except StopIteration:
                print(self.steamId, "Get new profile URL failed.")
                # 如果上述try中没有得到，那么就用原来的profileURL
                newProfileURL = self.profileURL
            for w in l_wantedData:
                rightCol = self.profilePage.find("div", class_="profile_rightcol")
                if rightCol:  # 如果右侧栏存在
                    # games和其余数据定位目录不同
                    if w == "games":
                        URL = newProfileURL + "/games/?tab=all"
                    else:
                        URL = newProfileURL + f"/{w}/"
                    wanted_a = rightCol.find("a", href=URL)  # 定位目标的到具体目录
                    if wanted_a:
                        wantedElement_span = wanted_a.find("span", class_="profile_count_link_total")
                        if wantedElement_span:
                            wantedElement = wantedElement_span.text.strip()
                        else:
                            wantedElement = wanted_a.find("div", class_="value").text.strip()
                    else:
                        wantedElement = "NO Data"
                else:
                    wantedElement = "NO Data"
                d_rightColList[w] = wantedElement
        else:
            pass
        return d_rightColList["badges"], d_rightColList["games"], d_rightColList["friends"], \
               d_rightColList["groups"], d_rightColList["screenshots"], d_rightColList["recommended"]

    # 近两周玩的游戏

    # achievements
    def getAchievements(self, appId, d_GlobalAchievements):
        d_USerAchievement = dict()  # Achievements: [Score, Unlock date, Unlock Year, Week, Status]
        achievementURL = f"https://steamcommunity.com/profiles/{self.steamId}/stats/{appId}/?tab=achievements"
        AchievementResp = requests.get(achievementURL)
        if not AchievementResp or d_GlobalAchievements.get("No Data"):  # 如果此游戏没有成就系统，like Dota2
            # Achievements: [Score, Unlock date, Unlock Year, Week, Status]
            d_USerAchievement["No achievements"] = ["No data", "No data", "No data", "No data", "No data"]
        else:
            achievementPage = BeautifulSoup(AchievementResp.text, "html.parser")
            divs = achievementPage.find_all("div", class_="achieveRow")
            if divs:
                for div in divs:
                    # achievementName
                    achievementName = div.find("h3", class_="ellipsis").text.strip()
                    # 如果有"XX个成就隐藏"字段则表示成就获取完毕，跳出循环
                    if achievementName.find("hidden achievements remaining") != -1 or \
                            achievementName.find("hidden achievement remaining") != -1:
                        break
                    # score
                    score = d_GlobalAchievements[achievementName]
                    # unlockTime
                    unlockTime = div.find("div", class_="achieveUnlockTime")
                    if unlockTime is None:
                        unlockTime = "Locked"
                    else:  # 如果成就解锁，修改unlockTime格式
                        unlockTime = unlockTime.text.strip().strip("Unlocked ").split("@")
                        unlockTimeFormat = unlockTime[0].strip().split(",")
                        if len(unlockTimeFormat) == 2:
                            unlockTime = unlockTimeFormat[1].strip(" ") + '/' + \
                                         monthTransDic[unlockTimeFormat[0].split(" ")[1]] + '/' + \
                                         unlockTimeFormat[0].split(" ")[0] + ' ' + \
                                         timeTrans(unlockTime[1].strip())
                        else:  # 如果是本年度解锁的评论，则需要加上年份
                            today = datetime.datetime.today()
                            unlockTime = str(today.year) + '/' + \
                                         monthTransDic[unlockTimeFormat[0].split(" ")[1]] + '/' + \
                                         unlockTimeFormat[0].split(" ")[0] + ' ' + \
                                         timeTrans(unlockTime[1].strip())
                    # 按照日期判断星期，是否为工作日。如果有日期，则取得星期数
                    if unlockTime != "Locked":
                        time_split = unlockTime.split(' ')[0].split('/')
                        unlockYear = time_split[0]
                        week = datetime.date(int(time_split[0]), int(time_split[1]), int(time_split[2])).isoweekday()
                        # 判断是否为工作日的睡眠时间（非周末00:00 ~ 08:00）
                        if week < 6 and int(unlockTime.split(' ')[1].split(':')[0]) <= 7:
                            status = 'U'
                        else:
                            status = 'N'
                    else:
                        unlockYear = unlockTime  # 也就是"Locked"
                        week = "L"
                        status = 'L'
                    d_USerAchievement[achievementName] = [score, unlockTime, unlockYear, week, status]
                # 检查是否用脚本解锁成就
                self.checkAchievementsUnlock(d_USerAchievement)
            else:
                # Achievements: [Score, Unlock date, Unlock Year, Week, Status]
                d_USerAchievement["No data"] = ["No data", "No data", "No data", "No data", "No data"]
        AchievementResp.close()
        return d_USerAchievement

    # 脚本成就解锁检测, 也可用于遍历用户成就字典
    @ staticmethod
    def checkAchievementsUnlock(d_userAchievement):
        counter = int(0)  # 查看解锁时间相同的成就个数
        tmp = "Empty"  # 暂时存放上一个成就解锁时间的变量
        for key, value1 in d_userAchievement.items():
            if key == "No achievements" or value1[-1] == 'L':
                break
            elif value1[1] != tmp:
                tmp = value1[1]
            elif value1[1] == tmp:
                counter += 1
                # 如果判定成就解锁时间相同
                if counter == 2:
                    # 则遍历成就解锁字典，把status全部换成E, 表示异常
                    for _, value2 in d_userAchievement.items():
                        value2[-1] = 'E'
                    break
        return d_userAchievement

    # 开启请求resp
    def getProfilePage(self):
        profileResp = requests.get(self.profileURL)
        profilePage = BeautifulSoup(profileResp.text, "html.parser")
        # 返回resp， BEAUTIFULSOUP.html.parser后的树状体
        return profileResp, profilePage

    # 关闭开启的请求resp
    def closeProfileResp(self):
        self.profileResp.close()


class Game:
    def __init__(self, title, appId, path):
        self.title = title
        self.appId = appId
        self.path = path + "/{}".format(title)
        self.jsonFileNum = 0  # 此游戏的json后缀文件个数, 初始化为0
        self.d_Users = dict()  # 此游戏全部用户数据的字典
        self.l_GlobalAchievements = self.getGlobalAchievement()  # 全球成就解锁状态的列表
        self.d_NormalizedGlobalAchievements = self.normalizedGlobalAchievements()  # 按照全球成就解锁标准化后的成就名和分数的字典

    # 取得此游戏的json后缀文件个数
    def getJsonFileNum(self):
        path = r'{}'.format(self.path)
        # self.jsonFileNum = len(os.listdir(path))
        for l in os.listdir(path):
            if l.endswith(".json"):
                self.jsonFileNum += 1

    # 取得成就的全球百分比数据
    def getGlobalAchievement(self):
        globalAchievementUrl = f"https://steamcommunity.com/stats/{self.appId}/achievements/"
        globalAchievementResp = requests.get(globalAchievementUrl)
        globalAchievementPage = BeautifulSoup(globalAchievementResp.text, "html.parser")
        divs = globalAchievementPage.find_all("div", class_="achieveRow")

        l_globalAchievement = list()
        for div in divs:
            achievement_title = div.find("h3").text.strip()
            achievement_percent = div.find("div", class_="achievePercent").text
            l_globalAchievement.append([achievement_title, achievement_percent])

        globalAchievementResp.close()
        self.l_GlobalAchievements = l_globalAchievement
        return l_globalAchievement

    # 数据标准化
    @staticmethod
    def minMaxNormalization(l_GlobalAchievements):
        # 2-1. 进行 1 - ratio 的操作
        for l in l_GlobalAchievements:
            l[1] = 1 - (float(l[1].strip("%")) * 0.01)
        # 2-2. 选取最值，均在列表的两端
        min = l_GlobalAchievements[0][1]
        max = l_GlobalAchievements[-1][1]
        # 3. 最后进行标准化计算（min_max_normalization），但数据会变成[0，1]区间
        for l in l_GlobalAchievements:
            l[1] = round((l[1] - min) / (max - min), 2)  # 保留小数点后2位数
        # 匹配成就名和score
        dic = dict()
        for l in l_GlobalAchievements:
            dic[l[0]] = l[1]

        return dic

    # 得到标准化后的成就字典
    def normalizedGlobalAchievements(self):
        if len(self.l_GlobalAchievements) != 0:
            d_GlobalAchievements = self.minMaxNormalization(self.l_GlobalAchievements)
        else:
            d_GlobalAchievements = {"No Data": "No Data"}
        return d_GlobalAchievements

    # 按照Score = 0 来修正游戏总时长
    def hoursAdjust(self):
        # 声明一个字典，用来存放读取到的文件中的数据，fileCount: Xth csv file list
        d_TotalUserData = dict()
        for fileNum in range(1, self.jsonFileNum + 1):
            # f"{self.title}_{f}Achievements.csv"
            with open(f"{self.title}_{fileNum}Achievements.csv", mode='r', encoding='utf-8') as f:
                csvReader = csv.reader(f)
                listOfRows = list(csvReader)
                d_TotalUserData[f] = listOfRows
                f.close()
        # Score is in 15th list, Hours is in 1st list, Year is in 17th list.
        # 声明一个字典 d_YearHour。 Year: [Total Hours in year, user numbers, avg Total Hours in year]
        d_YearHour = dict()
        for r in range(2010, int(datetime.datetime.today().year) + 1):  # 创建key为2010~今年的字典
            d_YearHour[str(r)] = [0, 0, float(0)]

        startYearList = list()  # [steamId, Hours, Year]
        for _, lists in d_TotalUserData.items():
            for l in lists:
                # l[0] is steamId, l[1] is Hours, l[17] is Year
                if l[15] == "Score":
                    continue
                elif l[15] == "No data":
                    startYearList.append([l[0], "No data", "No data"])
                elif float(l[15]) == 0:
                    # 如果Score为0的成就没有解锁, 则判断Year是今年开始玩的，并赋值
                    if l[17] == "Locked":
                        startYearList.append([l[0], l[1], str(datetime.datetime.today().year)])
                        d_YearHour[str(datetime.datetime.today().year)][0] += float(l[1])
                        d_YearHour[str(datetime.datetime.today().year)][1] += 1
                    else:
                        startYearList.append([l[0], l[1], l[17]])
                        d_YearHour[l[17]][0] += float(l[1])
                        d_YearHour[l[17]][1] += 1
                elif l[17] == "Locked":
                    continue
                else:
                    pass

        for k, v in d_YearHour.items():
            if v[1] != 0:
                v[2] = round(v[0] / v[1], 2)
            else:
                pass
            print(k, v)

        startYearDic = dict()  # steamId: AdjustedTotalHours
        for s in startYearList:
            if s[-1] == "No data" or s[-1] == "Locked":
                adjustedHours = s[-1]
            elif float(s[-1]) <= 1990:  # 读取到异常的时间值
                adjustedHours = "No data"
            else:
                if s[1] == "unVisible":
                    adjustedHours = "unVisible"
                else:
                    adjustedHours = round(float(s[1]) * (d_YearHour["2022"][-1] / d_YearHour[s[-1]][-1]), 2)
            startYearDic[s[0]] = adjustedHours
        # {self.title}Achievements4
        with open(f"{self.title}_Achievements4.csv", mode='w', encoding='utf-8', newline='') as f:
            csvWriter = csv.writer(f)
            for _, lists in d_TotalUserData.items():
                for l in lists:
                    if l[0] == "Steam ID":
                        l.append("AdjustedTotalHour")
                    elif startYearDic.__contains__(l[0]):
                        l.append(startYearDic[l[0]])
                    else:
                        l.append(l[15])
                    csvWriter.writerow(l)
            f.close()


if __name__ == "__main__":
    timeStart = time.time()  # 用来计算下列循环所用事件，开始
    path = "C:/Users/JinCh/PycharmProjects/pythonProject/Steam/games"
    game = Game("CounterStrike_Global_Offensive", "730", path)  # 声明Game对象
    game.getJsonFileNum()
    fileNum = 1  # 指定第几个json文件
    with open(f"{game.title}_{fileNum}reviews.json", mode='r') as f:
        l_Reviews = json.load(f)
        f.close()

    # 声明一些在下面的for循环中使用的变量
    l_data = list()  # 用来装用户数据
    x = int(1)  # 用来确认循环次数
    for review in l_Reviews:
        user = User(review["steamid"], review["hours"], review["last_tow_weeks"], review["last_played"])
        d_UserAchievements = user.getAchievements(game.appId, game.d_NormalizedGlobalAchievements)
        for k, v in d_UserAchievements.items():  # k是成就名，v列表中保存的依次是：score, unlockDate, unlockYear, week, status
            steamId, hours, lastTwoWeeks, lasPlayed, lastPlayedYear, nationality, level, badges, games, friends, \
            groups, screenshots, recommended, ifDisorder = user.getMember()
            l_data.append([steamId, hours, lastTwoWeeks, ifDisorder, lasPlayed, lastPlayedYear, nationality, level,
                           badges, games, friends, groups, screenshots, recommended, k, v[0], v[1], v[2], v[3], v[4]])
        tmpTimeEnd = time.time()
        print(x, "/ {}, steamId: {}, current time cost:".format(len(l_Reviews), user.steamId),
              timeParser(tmpTimeEnd - timeStart))
        x += 1  # 每次循环结束时++
        user.closeProfileResp()  # 关闭上述用户的resp

    with open(f"{game.title}_{fileNum}Achievements.csv", mode='w', encoding='UTF-8', newline='') as f:
        csvWriter = csv.writer(f)
        csvWriter.writerow(["Steam ID", "Hours", "Last Two Weeks", "If disorder", "Last Played", "Last Played Year", "Nation",
                            "Level", "Badges", "Games", "Friends", "Groups", "ScreenShots", "Reviews", "Achievement",
                            "Score", "Unlock date", "Unlock Year", "Week", "Status"])
        for l in l_data:
            csvWriter.writerow(l)
        f.close()

    game.hoursAdjust()
    timeEnd = time.time()  # 用来计算下列循环所用事件，结束
    print("program completed! cost:", timeParser(timeEnd - timeStart))
