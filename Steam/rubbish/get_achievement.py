from imports import *
import data_normalization


def get_steamId(game_title, i):
    reviews_file = open(f"{game_title}_{i}reviews.json", mode="r", encoding='utf-8')
    reviews_list = json.load(reviews_file)
    steamId_list = []

    for review in reviews_list:
        steamId_list.append(review["steamid"])

    reviews_file.close()
    return steamId_list


# 将12小时表示的时间转换为24小时，
def time_trans(clock_12):
    """ clock_12 = "XX:XXam/pm"
        clock_24 = "XX:XX" """
    if clock_12.find("pm") != -1:
        clock_24 = str(int(clock_12.split(':')[0]) + 12) + ':' + clock_12.split(':')[1].strip("pm")
    else:
        clock_24 = clock_12.strip("am")

    return clock_24


def user_full_achievement(steamId_list, appId):
    """
    显示全部用户（包括没有开放和未获得）的成就
    :param steamId_list: 从json文件中拿到的用户id
    :param appId: 游戏id
    :return: steamId_list中记录的所有用户的成就
    """

    # 英文月份转换数字的字典
    month_trans_dic = {
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
    # 调用标准化模块
    global_achievement_normalized_dic = data_normalization.normalization(appId)

    print("getting user_full_achievements")

    lists = list()
    x = 0  # 判断用户列表中的第几位用户

    for steamId in steamId_list:
        # 取得用户国籍
        personal_url = f"https://steamcommunity.com/profiles/{steamId}/"
        personal_resp = requests.get(personal_url)
        personal_page = BeautifulSoup(personal_resp.text, "html.parser")

        nation_div = personal_page.find("div", class_="c")
        # 有的人是完全没有class_="c"
        if nation_div:
            visible = nation_div.text.split('\n')
            # nation赋值
            # 如果用户国籍可见，则取得，否则定义为不可见
            if len(visible) == 5:
                nation = visible[-1].strip('\t')
            else:
                nation = "unVisible"
        else:
            nation = "unVisible"

        # 等级
        level_span = personal_page.find("span", class_="friendPlayerLevelNum")
        if level_span:
            level = level_span.text
        else:
            level = "No Data"

        # 获取用于右侧栏信息
        userList = list()
        wantedData = ["badges", "games", "friends", "groups", "screenshots", "recommended"]
        for w in wantedData:
            rightCol = personal_page.find("div", class_="profile_rightcol")
            if rightCol:
                if w == "games":
                    URL = f"https://steamcommunity.com/profiles/{steamId}/games/?tab=all"
                else:
                    URL = f"https://steamcommunity.com/profiles/{steamId}/{w}/"
                wanted_a = rightCol.find("a", href=URL)
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
            userList.append(wantedElement)

        personal_resp.close()

        # 获取近两周玩的游戏

        # 取得用户成就
        achievement_url = f"https://steamcommunity.com/profiles/{steamId}/stats/{appId}/?tab=achievements"
        resp = requests.get(achievement_url)
        # 如果此游戏没有成就系统，like Dota2
        if not resp or global_achievement_normalized_dic.get("No Data"):
            lists.append([steamId, nation, level, userList[0], userList[1], userList[2], userList[3], userList[4], userList[5], "No achievements", "No data", "No data", "No data"])
            x += 1
            print(steamId, "(", x, "/", len(steamId_list), ") is Done!")
            continue
        else:
            achievement_page = BeautifulSoup(resp.text, "html.parser")
            divs = achievement_page.find_all("div", class_="achieveRow")

            if divs:
                for div in divs:
                    # achievement_title赋值
                    achievement_title = div.find("h3", class_="ellipsis").text.strip()
                    # 如果有"XX个成就隐藏"字段
                    if achievement_title.find("hidden achievements remaining") != -1 or \
                       achievement_title.find("hidden achievement remaining") != -1:
                        continue
                    # score赋值
                    score = global_achievement_normalized_dic[achievement_title]
                    unlock_time = div.find("div", class_="achieveUnlockTime")
                    # unlock_time赋值
                    if unlock_time is None:
                        unlock_time = "Locked"
                    # 修改时间显示
                    else:
                        unlock_time = unlock_time.text.strip().strip("Unlocked ").split("@")
                        unlock_time_format = unlock_time[0].strip().split(",")
                        # print(unlock_time_format)
                        if len(unlock_time_format) == 2:
                            unlock_time = unlock_time_format[1].strip(" ") + '/' + \
                                          month_trans_dic[unlock_time_format[0].split(" ")[1]] + '/' + \
                                          unlock_time_format[0].split(" ")[0] + ' ' + \
                                          time_trans(unlock_time[1].strip())
                        else:
                            today = datetime.datetime.today()
                            # 如果是本年度解锁的评论，则需要加上年份
                            unlock_time = str(today.year) + '/' + \
                                          month_trans_dic[unlock_time_format[0].split(" ")[1]] + '/' + \
                                          unlock_time_format[0].split(" ")[0] + ' ' + \
                                          time_trans(unlock_time[1].strip())

                            # 按照日期判断星期，是否为工作日
                            # 如果有日期，则取得星期数
                    if unlock_time != "Locked":
                        time_split = unlock_time.split(' ')[0].split('/')
                        week = datetime.date(int(time_split[0]), int(time_split[1]), int(time_split[2])).isoweekday()
                        # 判断是否为工作日的睡眠时间（非周末00:00 ~ 08:00）
                        if week < 6 and int(unlock_time.split(' ')[1].split(':')[0]) <= 7:
                            status = 'U'
                        else:
                            status = 'N'
                    else:
                        week = "L"
                        status = 'L'
                    # print(steamId, nation, level, userList[0], userList[1], userList[2], userList[3], userList[4], userList[5], achievement_title, score, unlock_time, week, status)
                    lists.append([steamId, nation, level, userList[0], userList[1], userList[2], userList[3], userList[4], userList[5], achievement_title, score, unlock_time, week, status])
            else:
                # print(steamId, nation, level, userList[0], userList[1], userList[2], userList[3], userList[4], userList[5], "No data", "No data", "No data", "No data")
                lists.append([steamId, nation, level, userList[0], userList[1], userList[2], userList[3], userList[4], userList[5], "No data", "No data", "No data", "No data", "No data"])

            resp.close()
            x += 1
            print(steamId, "(", x, "/", len(steamId_list), ") is Done!")

    return lists


# 老版本，未修改
def user_exist_achievement(steamId_list, appId):
    """
    只显示开放且获得的成就
    :param steamId_list: 从json文件中拿到的用于id
    :param appId: 游戏id
    :return: steamId_list中记录的所有用户的成就
    """
    print("getting user_exist_achievements")

    lists = list()

    for steamId in steamId_list:
        achievement_url = f"https://steamcommunity.com/profiles/{steamId}/stats/{appId}/?tab=achievements"

        resp = requests.get(achievement_url)
        if not resp:
            continue
        else:
            achievement_page = BeautifulSoup(resp.text, "html.parser")
            divs = achievement_page.find_all("div", class_="achieveRow")

            if divs:
                for div in divs:
                    achievement_title = div.find("h3", class_="ellipsis").text.strip()
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
                            unlock_time = unlock_time[1] + unlock_time_format[0] + str(today.year)  # 需要把int型年份转化为str
                    lists.append([steamId, achievement_title, unlock_time])
            else:
                continue

            resp.close()
            print(steamId, "is Done!")

    print("ALL Done!!!")

    return lists


def get_achievement_run(appId, game_title, file_count):
    """
    appId: 游戏编号
    game_title: 游戏标题
    i: 文件数
    """
    for file_num in range(1, file_count + 1):
        steamId_list = get_steamId(game_title, file_num)
        lists = user_full_achievement(steamId_list, appId)

        if f"{game_title}_{file_num}Achievements.csv":
            with open(f"{game_title}_{file_num}Achievements.csv", mode="w", newline='', encoding='utf-8') as f:
                csvwriter = csv.writer(f)
                csvwriter.writerow(["Steam ID", "Nation", "Level", "Badges", "Games", "Friends", "Groups", "ScreenShots", "Reviews", "Achievement", "Score", "Unlock date", "Week", "Status"])
                for l in lists:
                    csvwriter.writerow(l)
                f.close()

        print(game_title, file_num, "th file Done!")
