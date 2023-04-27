from get_achievement import get_achievement_run
import os
from csv import reader

# 打开获取到的TOP100游戏文件
with open(f'TOP 100 FPS.csv', encoding='utf-8', mode='r') as achievements_file:
    csvReader = reader(achievements_file)
    # Passing the cav_reader object to list() to get a list of lists
    gameList = list(csvReader)
print("get_top100_FPS finished!")

for g in gameList:
    # 检查游戏名称里面是否有非法符号
    if g[0].find(':') != -1:
        tmp_g = g[0].split(':')
        g[0] = tmp_g[0] + tmp_g[1]
    if g[0].find('*') != -1:
        tmp_g = g[0].split('*')
        g[0] = tmp_g[0] + tmp_g[1]
    path = r'C:\Users\JinCh\PycharmProjects\pythonProject\Steam\games\{}'.format(g[0])
    os.chdir(path)
    fileCount = len(os.listdir(path))
    if fileCount == 0:
        continue
    else:
        print(g[0], fileCount)

        get_achievement_run(g[1], g[0], fileCount)

        print(g[0], "Finished!!!")
