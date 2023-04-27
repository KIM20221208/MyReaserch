import json
import csv


def file_data(game_title, x):
    csv_file = open(f'{game_title}_reviews.csv', 'w', newline='', encoding='utf-8')
    # 4.1根据文件对象  生成读写器
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["id", "author", "date", "steamid", "hours", "last_two_weeks",
                         "content", "recommended", "gameName"])

    for i in range(1, x + 1):
        json_file = open(f'{game_title}_{i}reviews.json', 'r')
        # 3.取出数据 : 1.表头 2. 内容
        json_list = json.load(json_file)
        # 3.1获取表头所需要的数据
        # sheet_title = json_list[0].keys()
        # 3.2 取所有内容
        json_values = []
        for dict in json_list:
            json_values.append(dict.values())
        # 4.2 写入表头
        # csv_writer.writerow(sheet_title)
        # 4.3 写入内容
        csv_writer.writerows(json_values)
        # 5.关闭文件
        json_file.close()

    csv_file.close()
    print(game_title, "Done!!!")
