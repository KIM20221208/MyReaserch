import csv
import os

gameTitle = "CounterStrike_Global_Offensive"
path = r"C:/Users/JinCh/PycharmProjects/pythonProject/Steam/games/{}".format(gameTitle)
os.chdir(path)
fileCount = int(len(os.listdir(path)) / 3)  # 得到文件个数
d_TotalUserData = dict()  # {fileCount: Xth csv file list}

for f in range(1, fileCount + 1):
    with open(f"{gameTitle}_{f}Achievements3.2.csv", mode='r', encoding='utf-8') as f:
        csvReader = csv.reader(f)
        listOfRows = list(csvReader)
        d_TotalUserData[f] = listOfRows
        f.close()
# Score is in 10th list, Hours is in 15th list, Year is in 19th list.
# d_YearHour = [Year]: [Total Hours in year, user numbers, avg Total Hours in year]
d_YearHour = {
    "2022": [0, 0, 0],
    "2021": [0, 0, 0],
    "2020": [0, 0, 0],
    "2019": [0, 0, 0],
    "2018": [0, 0, 0],
    "2017": [0, 0, 0],
    "2016": [0, 0, 0],
    "2015": [0, 0, 0],
    "2014": [0, 0, 0],
    "2013": [0, 0, 0],
    "2012": [0, 0, 0],
    "2011": [0, 0, 0],
    "2010": [0, 0, 0]
}

startYearList = list()  # [steamId, Hours, Year]
for _, lists in d_TotalUserData.items():
    for l in lists:
        # l[0] is steamId, l[15] is Hours, l[19] is Year
        if l[10] == "Score" or l[19] == "Locked":
            continue
        elif l[10] == "No data":
            startYearList.append([l[0], l[15], l[19]])
        elif float(l[10]) == 0:
            # 如果Score为0的成就没有解锁
            d_YearHour[l[19]][0] += float(l[15])
            d_YearHour[l[19]][1] += 1
            startYearList.append([l[0], l[15], l[19]])
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
    if s[-1] == "No data":
        adjustedHours = "No data"
    elif s[-1] == "Locked":
        adjustedHours = "Locked"
    elif float(s[-1]) <= 1990:
        adjustedHours = "No data"
    else:
        if s[1] == "unVisible":
            adjustedHours = "unVisible"
        else:
            adjustedHours = round(float(s[1]) * (d_YearHour["2022"][-1] / d_YearHour[s[-1]][-1]), 2)
    startYearDic[s[0]] = adjustedHours

with open(f"{gameTitle}Achievements4.csv", mode='w', encoding='utf-8', newline='') as f:
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
