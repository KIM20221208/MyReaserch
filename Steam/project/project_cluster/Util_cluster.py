import csv
import os
from Util_achievements import Game


class Achievement:
    def __init__(self, Title, score, unlockDate, week, status):
        self.Title = Title
        self.score = score
        self.unlockDate = unlockDate
        self.week = week
        self.status = status

    def getMem(self):
        return self.Title, self.score, self.unlockDate, self.week, self.status


class User:
    def __init__(self, steamId, hours, lastTwoWeeks, ifDisorder, lastPlayed, nation, level,
                 badges, games, friends, groups, screenshots, reviews, ATH, totalScore, fromRank):
        self.steamId = steamId
        self.hours = float(hours)
        self.lastTwoWeeks = float(lastTwoWeeks)
        self.ifDisorder = int(ifDisorder)
        self.lastPlayed = lastPlayed
        self.nation = nation
        self.level = level
        self.badges = badges
        self.games = games
        self.friends = friends
        self.groups = groups
        self.screenshots = screenshots
        self.reviews = reviews
        self.achievements = list()  # list: [c_Achievement1, c_Achievement2...]
        self.ATH = ATH
        self.totalScore = totalScore
        self.fromRank = int(fromRank)

        self.scoreCount = int(0)
        self.scoreSum = float(0)
        self.status_U_Count = int(0)

    def GetMem(self):
        return self.steamId, self.hours, self.lastTwoWeeks, self.ifDisorder, self.lastPlayed, self.nation, self.level, \
               self.badges, self.games, self.friends, self.groups, self.screenshots, self.reviews, self.ATH, \
               self.scoreCount, round(self.scoreSum, 2), self.status_U_Count

    def TypeTrans(self):
        try:
            self.level = int(self.level)
        except ValueError:
            self.level = int(0)
        try:
            self.badges = int(self.badges)
        except ValueError:
            self.badges = int(0)
        try:
            self.games = int(self.games)
        except ValueError:
            self.games = int(0)
        try:
            self.friends = int(self.friends)
        except ValueError:
            self.friends = int(0)
        try:
            self.groups = int(self.groups)
        except ValueError:
            self.groups = int(0)
        try:
            self.screenshots = int(self.screenshots)
        except ValueError:
            self.screenshots = int(0)
        try:
            self.reviews = int(self.reviews)
        except ValueError:
            self.reviews = int(0)
        try:
            self.ATH = float(self.ATH)
        except ValueError:
            self.ATH = float(0)

    def Aggregate(self):
        for achievement in self.achievements:
            try:
                if achievement.unlockDate != "Locked":
                    self.scoreCount += 1
                    self.scoreSum += float(achievement.score)
                    if achievement.status == "U":
                        self.status_U_Count += 1
            except ValueError:
                print("读取游戏 {} 中用户 {} 时发生 \"ValueError\" 错误。".format(self.fromRank, self.steamId))
        self.scoreSum = round(self.scoreSum / self.totalScore, 2)
        if self.status_U_Count != 0:
            self.status_U_Count = round(self.status_U_Count / self.scoreCount, 2)

    def SelectMem(self):
        return self.lastTwoWeeks, self.ATH, self.scoreSum, self.status_U_Count, \
               self.level, self.badges, self.games, self.friends, self.groups, self.screenshots, self.reviews


class AGame:
    def __init__(self, title, appId):
        self.title = title
        self.appId = appId


def Cleaning(l_type):
    l_userDeleter = list()
    l_tmp = l_type
    for i in range(len(l_tmp)):
        if l_tmp[i].achievements[0].Title == "No data":
            l_userDeleter.append(i)
        else:
            check = True
            for j in l_tmp[i].achievements:
                if j.status == 'E':
                    l_userDeleter.append(i)
                    check = False
                    break
            if check:
                l_tmp[i].Aggregate()
    tmp = int(0)
    for i in l_userDeleter:
        # print(l_tmp[i - tmp].steamId, l_tmp[i - tmp].achievements[0].Title)
        del l_tmp[i - tmp]
        tmp += 1
    return l_tmp


def Selecting(l_type):
    l_Selected = list()
    for row in l_type:
        lastTwoWeeks, ATH, scoreSum, status_U_Count, \
        level, badges, games, friends, groups, screenshots, reviews = row.SelectMem()
        l_Selected.append([lastTwoWeeks, ATH, scoreSum, status_U_Count,
                           level, badges, games, friends, groups, screenshots, reviews])
    return l_Selected


def GameListReader(fileName):
    d_Type = dict()
    with open(fileName, mode='r', encoding='UTF-8') as file:
        csvReader = csv.reader(file)
        for row in csvReader:
            game = AGame(title=row[1], appId=row[2])
            d_Type[row[0]] = game

    return d_Type


def GameFileReader(d_Type):
    l_Total_Users = list()
    for rank, aGame in d_Type.items():
        path = "C:/Users/JinCh/PycharmProjects/pythonProject/Steam/games/data_ver4/{}".format(aGame.title)
        os.chdir(path)
        # 拿到成就分数总和
        newGame = Game(title=aGame.title, appId=aGame.appId, path=path)
        totalScore = float(0)
        for _, v in newGame.d_NormalizedGlobalAchievements.items():
            totalScore += v

        # 读取_achievements4.csv文件数据到list：[c_Users1, c_Users2...]
        with open("{}_Achievements4.csv".format(aGame.title), mode='r', encoding='UTF-8') as file:
            l_Users = list()  # 存放User类的列表
            csvReader = csv.reader(file)
            for row in csvReader:
                if row[0] == "Steam ID":
                    continue
                c_User = User(steamId=row[0], hours=row[1], lastTwoWeeks=row[2], ifDisorder=row[3], lastPlayed=row[4],
                              nation=row[5], level=row[7], badges=row[8], games=row[9], friends=row[10], groups=row[11],
                              screenshots=row[12], reviews=row[13], ATH=row[-1], totalScore=totalScore, fromRank=rank)
                c_User.TypeTrans()
                c_Achievements = Achievement(Title=row[14], score=row[15], unlockDate=row[16], week=row[18],
                                             status=row[19])
                c_User.achievements.append(c_Achievements)
                # 如果是循环中的第一个用户
                if len(l_Users) == 0:
                    l_Users.append(c_User)
                # 从第二个用户开始
                else:
                    # 如果此次循环中的用户和上次的是同一个人
                    if c_User.steamId == l_Users[-1].steamId:
                        # 则用户列表不添加新用户，成就列表添加此次循环中的成就
                        l_Users[-1].achievements.append(c_Achievements)
                    else:
                        # 如果不是同一个人， 则添加为新用户，并且为此用户添加成就列表
                        l_Users.append(c_User)
            file.close()
        for user in l_Users:
            l_Total_Users.append(user)
        print("{}读取完毕, 包含用户 {}".format(aGame.title, len(l_Users)))

    l_Total_Users_Cleaned = Cleaning(l_Total_Users)
    print("after cleaning, Total usable data is: {}".format(len(l_Total_Users_Cleaned)))
    return l_Total_Users_Cleaned, Selecting(l_Total_Users_Cleaned)


if __name__ == "__main__":
    d_Games = GameListReader("gameList.csv")
    l_Total_Users_Cleaned, l_P_Total_Users = GameFileReader(d_Games)

    for i in range(len(l_Total_Users_Cleaned)):
        if l_Total_Users_Cleaned[i].fromRank == 3:
            print(l_P_Total_Users[i])
        elif l_Total_Users_Cleaned[i].fromRank == 6:
            break
