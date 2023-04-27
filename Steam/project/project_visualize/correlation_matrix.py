import matplotlib.pyplot as plt
import numpy as np
import csv

value = list()
with open("123.csv", mode='r', encoding='UTF-8') as file:
    csvReader = csv.reader(file)
    for row in csvReader:
        value.append(row)

int_value = list()
for row in value:
    tmp = list()
    for e in row:
        tmp.append(float(e))
    int_value.append(tmp)
    print(tmp)

np_matrix = np.array(int_value)
mat = np.arange(0, 100).reshape(10, 10)

print(mat.shape, type(mat[0][0]), mat[0][0])
print(np_matrix.shape, type(np_matrix[0][0]), np_matrix[0][0])

plt.matshow(np_matrix, cmap='viridis')
plt.yticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], ["Rank", "P$_{1}$", "P$_{2}$", "P$_{3}$", "P$_{4}$", "P$_{5}$",
                                                        "P$_{6}$", "P$_{7}$", "P$_{8}$", "P$_{9}$", "P$_{10}$",
                                                        "P$_{11}$", "Ru"])
plt.colorbar()
for i in range(len(np_matrix)):
    for j in range(len(np_matrix[i])):
        plt.text(j, i, round(np_matrix[i][j], 3), ha="center", va="center", color="black")
users_feature_names = np.array(
        ["Rank", "P$_{1}$", "P$_{2}$", "P$_{3}$", "P$_{4}$", "P$_{5}$", "P$_{6}$", "P$_{7}$", "P$_{8}$", "P$_{9}$",
         "P$_{10}$", "P$_{11}$", "Ru"])
plt.xticks(range(13), users_feature_names)
plt.show()