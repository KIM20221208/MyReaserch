import csv

originalData = list()
with open("TimeComparing.csv", mode='r', encoding='UTF-8') as file:
    csvReader = csv.reader(file)
    for row in csvReader:
        originalData.append(row)
    file.close()

processedData = dict()
for row in originalData:
    tmp = row[0].split(';')
    year = float(tmp[0].split("-")[0])
    num = float(tmp[1])
    if ProcessedData.__contains__(year):
        ProcessedData[year] += num
    else:
        ProcessedData[year] = num

with open("TimeComparing.csv", mode='w', encoding='UTF-8', newline='') as file:
    csvWriter = csv.writer(file)
    for row in originalData:
        tmp = row[0].split(';')
        csvWriter.writerow([tmp[0], tmp[1], tmp[2]])
    file.close()
