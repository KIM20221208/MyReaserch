# word cloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import csv

l_gameTags = list()
with open("total62_game_tags.csv", mode='r', encoding='UTF-8') as file:
    csvReader = csv.reader(file)
    for row in csvReader:
        l_gameTags.append(row)

string = str()

d_gameTags = dict()
for game in l_gameTags:
    for j in range(len(game) - 1):
        if not d_gameTags.__contains__(game[j]):
            d_gameTags[game[j]] = float(game[-1])
        else:
            d_gameTags[game[j]] += float(game[-1])

for k, v in d_gameTags.items():
    print(k)
    for i in range(int(v * 100)):
        if k.find(' ') != -1:
            l_tmp = k.split(' ')
            for j in range(len(l_tmp)):
                string += l_tmp[j]
        elif k.find('-') != -1:
            l_tmp = k.split('-')
            for j in range(len(l_tmp)):
                string += l_tmp[j]
        else:
            string += k
        string += ','
for k, v in d_gameTags.items():
    print(v)

print(string)

w = WordCloud(width=1000, height=700, background_color='white', font_path='msyh.ttc', collocations=False)
w.generate(string)
w.to_file('output_total62.png')
