from achievements_reform import achievements_reform_run
import os

gameTitle = "CounterStrike_Global_Offensive"
appID = "730"
path = r"C:/Users/JinCh/PycharmProjects/pythonProject/Steam/games/{}".format(gameTitle)
os.chdir(path)
fileCount = int(len(os.listdir(path)) / 2)  # 得到文件个数

achievements_reform_run(game_title=gameTitle, appId=appID, file_count=fileCount)
