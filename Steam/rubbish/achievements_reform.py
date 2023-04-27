from imports import *
from csv import reader
import data_normalization


def achievements_reform_run(game_title, appId, file_count):
    d_FileUser = dict()
    for file_num in range(1, file_count + 1):
        # 参数
        x = 0  # id编号
        achievement_count = 0
        ACHIEVEMENT_NUMBER = len(data_normalization.get_global_achievement(appId))  # 游戏成就数量
        r = 1  # 脚本成就解锁用参数

        with open(f'{game_title}_{file_num}Achievements.csv', mode='r', encoding='utf-8') as achievements_file:
            csv_reader = reader(achievements_file)
            # Passing the cav_reader object to list() to get a list of lists
            list_of_rows = list(csv_reader)

        json_file = open(f'{game_title}_{file_num}reviews.json', mode='r')
        json_list = json.load(json_file)
        json_file.close()

        for row in list_of_rows:
            if row[0] == "Steam ID":
                row.extend(["Country", "Hours", "Last Two Weeks", "Last Played", "Last Played year", "Year", "If disorder"])
            # 检查steamid是否对应
            else:
                # country
                if row[1] == "unVisible":
                    country = "unVisible"
                else:
                    country = row[1].split(',')[-1].strip
                # Hours
                hours = round(int(json_list[x]["hours"]) / 60, 2)
                # Last Two Weeks
                lastTwoWeeks = round(int(json_list[x]["last_tow_weeks"]) / 60, 2)
                # Last Played
                date = json_list[x]["last_played"]
                l_date = date.split('-')
                # Last Played Year
                y = "20" + l_date[-1]
                m = l_date[1]
                d = l_date[0]
                lastPlayed = y + '/' + m + '/' + d
                # 按照成就数量重新赋值steamId
                if row[9] == "No data":
                    # row[0] = json_list[x]["steamid"]
                    # row[0] = x
                    row.append("No data")  # 补一个元素
                    x += 1
                else:
                    # row[0] = json_list[x]["steamid"]
                    # row[0] = x
                    achievement_count += 1
                    if achievement_count == ACHIEVEMENT_NUMBER:
                        x += 1
                        achievement_count = 0
                # year: 成就获取年份
                if len(row[11].split('/')) == 3:
                    year = row[11].split('/')[0]
                else:
                    year = row[11]  # No data
                # ifDisorder: 初步判断是否为游戏障碍用户
                if lastTwoWeeks >= 70.98:
                    ifDisorder = 2
                elif 42.7 <= lastTwoWeeks:
                    ifDisorder = 1
                elif lastTwoWeeks < 42.7:
                    ifDisorder = 0
                else:
                    ifDisorder = "No data"
                row.extend([country, hours, lastTwoWeeks, lastPlayed, y, year, ifDisorder])
            print(x, row)

        # 判断哪些用户是用脚本解锁的成就
        while True:
            """if list_of_rows[r][4] != "No data" and list_of_rows[r][4] == list_of_rows[r + 1][4]:
                # 如果判定到了用户，则将他的status状态全部变为‘E’
                for a in range(ACHIEVEMENT_NUMBER):
                    print(list_of_rows[r])
                    # list_of_rows[row][6] = 'E'
                    r += 1"""
            if list_of_rows[r][11] != "No data" and list_of_rows[r][11] != "Locked" \
                    and list_of_rows[r][11] == list_of_rows[r + 1][11] and list_of_rows[r + 1][11] == list_of_rows[r + 2][11]:
                Error_time = list_of_rows[r][11]
                for a in range(r, r + ACHIEVEMENT_NUMBER):
                    if list_of_rows[a][11] == Error_time:
                        list_of_rows[a][13] = 'E'
                        print(list_of_rows[a][0], list_of_rows[a][2], list_of_rows[a][11], list_of_rows[a][6])
                        print(a)
                r += ACHIEVEMENT_NUMBER
            else:
                r += 1
            if r == len(list_of_rows):
                break

        with open(f"{game_title}_{file_num}Achievements3.2.csv", mode="w", newline='', encoding='utf-8') as f:
            csvWriter = csv.writer(f)
            for item in list_of_rows:
                csvWriter.writerow(item)
            f.close()
