"""整合所有模块
    运行区域"""
from csv import reader
from get_reviews import get_reviews_run


# 各种参数
file_count = 0  # 文件计数器
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
        # 获取评论
        get_reviews_run(g[1], g[0])
"""     # 把评论整合成单个csv文件
        file_data(g[0], file_count)
        # 获取用户数据
        get_achievement_run(g[1], g[0], file_count)
        # 加工数据
        achievements_reform_run(g[0], g[1], file_count)"""
