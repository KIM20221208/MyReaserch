"""整合所有模块
    运行区域"""
import os
from csv import reader
from util import get_reviews_run

# 打开获取到的TOP100游戏文件
with open(f'TOP 100 FPS.csv', encoding='utf-8', mode='r') as achievements_file:
    csvReader = reader(achievements_file)
    # Passing the cav_reader object to list() to get a list of lists
    gameList = list(csvReader)
print("get_top100_FPS finished!")

# 开始获取用户数据
for g in gameList:
    if g[0] == "Game Title":
        continue
    else:
        # 检查游戏名称里面是否有非法符号
        if g[0].find(':') != -1:
            tmp_g = g[0].split(':')
            g[0] = tmp_g[0] + tmp_g[1]
        if g[0].find('*') != -1:
            tmp_g = g[0].split('*')
            g[0] = tmp_g[0] + tmp_g[1]
        # 按照游戏名创建新建文件夹
        path = r'C:/Users/JinCh/PycharmProjects/pythonProject/Steam/games/data_ver4'
        os.chdir(path)
        os.makedirs(name=g[0])
        # 把下列数据保存到对应路径
        path1 = './{}'.format(g[0])
        os.chdir(path1)
        # 获取评论
        get_reviews_run(str(g[1]), g[0])
        print("\n", g[0], "DONE!!!\n")
