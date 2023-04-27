import csv
import os

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
from matplotlib import style
from scipy.linalg import svd
from kneed import KneeLocator
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_selection import VarianceThreshold
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA
from sklearn.decomposition import _kernel_pca
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

import Util_cluster as Cluster


# 归一化
def Normalize(np_Type):
    scaler = MinMaxScaler()
    scaler.fit(np_Type)
    return scaler.transform(np_Type)


# 标准化
def Standard(np_Type):
    scaler = StandardScaler()
    scaler.fit(np_Type)
    return scaler.transform(np_Type)


# 方差过滤
def VarianceFilter(np_Type):
    selector = VarianceThreshold(threshold=0)  # 方差为选择为0，也就是过滤只有一个值的属性
    filtered_np_Type = selector.fit_transform(np_Type)
    return filtered_np_Type


# svd分析
def SVD_Analyze(np_Type, threshold):
    U, s, Vh = svd(np_Type)
    # print(s.shape, s)
    # x is component
    x = int(0)
    for i in range(s.shape[0]):
        percent = np.sum(np.square(s[:i + 1])) * 1.0 / np.sum(np.square(s))
        if percent >= threshold:
            x = i + 1
            print("SVD分析后，在阈值为 [{}] 的前提下，奇异值个数为：{}".format(threshold, x))
            break
    return x


# 显示PCA成分分析细节
def pcaDetails(pca):
    print("PCA成分数：{}".format(pca.components_.shape))
    print("PCA成分图：\n{}".format(pca.components_))

    plt.matshow(pca.components_, cmap='viridis')
    plt.yticks([0, 1, 2], ["First component", "Second component", "Third component"])
    plt.colorbar()
    for i in range(len(pca.components_)):
        for j in range(len(pca.components_[i])):
            plt.text(j, i, round(pca.components_[i][j], 3), ha="center", va="center", color="black")
    users_feature_names = np.array(
        ["Last Two Weeks", "AdjustedTotalHour", "sum(Score)", "count(Status)", "Level", "Badges",
         "Games", "Friends", "Groups", "ScreenShots", "Reviews"])
    plt.xticks(range(11), users_feature_names, rotation=60, ha='left')
    plt.xlabel("Feature")
    plt.ylabel("Principle component")


# PCA分析，降维
def PCA_Decomposition(np_Type, component):
    pca = PCA(n_components=component)
    pca.fit(np_Type)
    np_Type_Pca = pca.transform(np_Type)
    print("原始数据 shape； {}".format(str(np_Type.shape)))
    print("PCA降维后数据 shape； {}".format(str(np_Type_Pca.shape)))
    # print(users_pca1)
    pcaDetails(pca)
    return np_Type_Pca


# KPCA分析，降维
def KPCA_Decomposition(np_Type, component):
    Kpca = _kernel_pca.KernelPCA(n_components=component, kernel="sigmoid", gamma=15)
    Kpca.fit(np_Type)

    np_Type_Kpca = Kpca.transform(np_Type)
    print("原始数据 shape； {}".format(str(np_Type.shape)))
    print("KPCA降维后数据 shape； {}".format(str(np_Type_Kpca.shape)))
    return np_Type_Kpca


# LDA降维，数据可视化
def LDA_Discriminant(np_Type, np_cluster, component):
    lda = LinearDiscriminantAnalysis(n_components=component)
    lda.fit(np_Type, np_cluster)
    np_Type_Lda = lda.transform(np_Type)
    return np_Type_Lda


# 按照数据特征，分为3个主成分：时间，睡眠，社交
def My_Decomposition(np_Type):
    print("\n\n开始计算按照数据特征的降维：")
    splitted = np.split(np_Type, [3, 4], axis=1)
    # print("分离前数据：\n{}, \n{}".format(np_Type[0], np_Type[1]))
    # print("分离后数据：\n", splitted[0][0], splitted[1][0], splitted[2][0])
    playtime_component = PCA_Decomposition(splitted[0], 1)
    pursuit_component = splitted[1]
    social_component = PCA_Decomposition(splitted[2], 1)
    # print("进行各自PCA降维后的结果为：\n", playtime_component[0], pursuit_component[0], social_component[0])
    np_Type_new = np.hstack((playtime_component, pursuit_component, social_component))
    # print("进行数组合并后的新数组为：\n", np_Type_new[0])

    return np_Type_new


# T-SNE降维
def Tsne(np_Type):
    tsne = TSNE(n_components=2)
    decomposition = tsne.fit_transform(np_Type)
    x_axis = decomposition[:, 0]
    y_axis = decomposition[:, 1]

    plt.scatter(x_axis, y_axis)


# MDS降维
def Mds(np_Type):
    mds = MDS(n_components=3)
    np_Type_MDS = mds.fit_transform(np_Type)
    print("原始数据 shape； {}".format(str(np_Type.shape)))
    print("Mds降维后数据 shape； {}".format(str(np_Type_MDS.shape)))
    return np_Type_MDS


# K-means聚类
def K_Means(np_Type, n_Clusters):
    print("\n\nK-means聚类：")
    kmeans = KMeans(n_clusters=n_Clusters, random_state=1)
    kmeans.fit(np_Type)
    # print("k-means聚类后的标签:\n {}".format(kmeans.labels_))
    return kmeans.labels_


# 凝聚聚类, linkage = 'average'
def Agglomerative(np_Type, linkage):
    print("\n\n凝聚聚类：")
    agg = AgglomerativeClustering(n_clusters=np_Type.shape[1], linkage=linkage)
    assignment = agg.fit_predict(np_Type)
    # print("凝聚聚类后的标签:\n {}".format(assignment))
    return assignment


def knee_point_search(x, y):
    # 转为list以支持负号索引
    x, y = x.tolist(), y.tolist()
    output_knees = []
    for curve in ['convex', 'concave']:
        for direction in ['increasing', 'decreasing']:
            model = KneeLocator(x=x, y=y, curve=curve, direction=direction, online=False)
            if model.knee != x[0] and model.knee != x[-1]:
                output_knees.append((model.knee, model.knee_y, curve, direction))

    if output_knees.__len__() != 0:
        print('发现拐点！')
        return output_knees
    else:
        print('未发现拐点！')


# DBSCAN
def Dbscan(np_Type, value):
    print("\n\nDBSCAN聚类：")
    k = np_Type.shape[1] * 2 - 1
    # k-neighbors
    neighbors = NearestNeighbors(n_neighbors=k)
    neighbors_fit = neighbors.fit(np_Type)
    distances, indices = neighbors_fit.kneighbors(np_Type)
    distances = np.sort(distances, axis=0)[:, 1]
    x_axis = np.arange(len(distances))
    style.use('seaborn-whitegrid')
    fig = plt.figure()
    axe = fig.add_subplot()
    axe.plot(x_axis, distances)

    """crook = KneeLocator(x=x_axis, y=distances, curve='convex', direction='increasing', online=False)"""

    knee_info = knee_point_search(x=x_axis, y=distances)
    eps = value  # according to ICIET2023, default value is 0.35.
    for point in knee_info:
        axe.scatter(x=point[0], y=point[1], c='r', marker='^')
        axe.annotate(text=f'{point[2]} {point[3]}', xy=(point[0] + 1, point[1]), fontsize=14)
        print("k-distances下的拐点为: [{},{}]".format(point[0], point[1]))
        # eps = point[1]
    # eps需要观察k-neighbors的拐点来设置，min_samples一般设置为维度 * 2
    min_samples = k + 1
    print("DBSCAN参数eps: {}, min_samples: {}".format(eps, min_samples))
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(np_Type)

    return clusters


def drawColorBar(l_Type):
    fig, axes = plt.subplots(2, 1)
    label = ["cluster -1", "cluster 0", "cluster 1", "cluster 2", "cluster 3", "cluster 4", "cluster 5", "cluster 6",
             "cluster 7", "cluster 8", "cluster 9"]

    bins = list()
    for num in range(len(l_Type) + 1):
        bins.append(num)
    nbin = len(bins) - 1
    cmap = cm.get_cmap('brg', nbin)
    norm = mcolors.BoundaryNorm(bins, nbin)
    im = cm.ScalarMappable(norm=norm, cmap=cmap)
    # 使用BoundaryNorm时,colorbar会自动按bins标出刻度.
    cbar4 = fig.colorbar(
        im, cax=axes[0], orientation='horizontal',
        label='colorbar with BoundaryNorm'
    )
    # axes[1].pie(x=l_Type, labels=label, color=cmap, norm=norm)


# 绘制3D散点图
def draw3DScatter(data_array, clustered_label):
    style.use('ggplot')
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection='3d')
    norm = plt.Normalize(vmin=np.min(clustered_label), vmax=np.max(clustered_label))
    # 以下声明坐标的操作，可以换成字典并以for循环按簇的数量进行动态声明
    d_cluster = dict()
    for num in clustered_label:
        if not d_cluster.__contains__(num):
            d_cluster[num] = {
                "x": list(),
                "y": list(),
                "z": list()
            }
        else:
            pass

    my_map = plt.get_cmap('brg', len(d_cluster.keys()))
    for row in range(data_array.shape[0]):
        d_cluster[clustered_label[row]]["x"].append(data_array[row][0])
        d_cluster[clustered_label[row]]["y"].append(data_array[row][1])
        d_cluster[clustered_label[row]]["z"].append(data_array[row][2])

    print("总样本数为{}:".format(data_array.shape[0]))
    l_num = list()
    for num, xyz in sorted(d_cluster.items()):
        print("聚类{}: {}".format(num, len(xyz["x"])))
        l_num.append(len(xyz["x"]))
        # ax1.scatter(kmeans.cluster_centers_[1][0], kmeans.cluster_centers_[1][1], kmeans.cluster_centers_[1][2],
                # c='b', marker='^', linewidths=2)
    drawColorBar(l_num)
    # ax2 = fig.add_subplot(212,)
    # ax2.plot(range(len(l_num)), l_num)
    for i in range(len(clustered_label)):
        if clustered_label[i] == -1:
            clustered_label[i] = len(d_cluster.keys())

    ax1.scatter(data_array[:, 0], data_array[:, 1], data_array[:, 2], c=clustered_label, cmap=my_map, marker='^')
    ax1.set_xlabel('x: 1st component')
    ax1.set_ylabel('y: 2nd component')
    ax1.set_zlabel('z: 3rd component')


def draw2DScatter(data_array, clustered_label, x):
    style.use('ggplot')
    fig = plt.figure()
    ax1 = fig.add_subplot()

    # 以下声明坐标的操作，可以换成字典并以for循环按簇的数量进行动态声明
    x0 = list()
    y0 = list()
    x1 = list()
    y1 = list()
    counter = int(0)
    for row in range(data_array.shape[0]):
        if clustered_label[row] == x:
            x0.append(data_array[row][0])
            y0.append(data_array[row][1])
        else:
            x1.append(data_array[row][0])
            y1.append(data_array[row][1])
            counter += 1
    print("样本总量为：{}\n聚类1中的样本共为：{}\n比例为：{}".format(data_array.shape[0], counter, counter / data_array.shape[0]))

    ax1.scatter(x0, y0, c='g', marker='^')
    # ax1.scatter(kmeans.cluster_centers_[0][0], kmeans.cluster_centers_[0][1], kmeans.cluster_centers_[0][2],
                # c='b', marker='^', linewidths=2)
    ax1.scatter(x1, y1, c='r', marker='o')
    # ax1.scatter(kmeans.cluster_centers_[1][0], kmeans.cluster_centers_[1][1], kmeans.cluster_centers_[1][2],
                # c='b', marker='^', linewidths=2)
    ax1.set_xlabel('x: 1st component')
    ax1.set_ylabel('y: 2nd component')


def calculate(l_users, np_cluster, x):
    l_tmp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    calculator = int(0)
    for i in range(len(np_cluster)):
        if np_cluster[i] != x:
            for j in range(len(l_tmp)):
                l_tmp[j] += l_users[i][j]
            calculator += 1
    print(l_tmp)
    print("Average:\nlastTwoWeeks, ATH, scoreSum status_U_Count, "
          "level, badges, games, friends, groups, screenshots, reviews\n",
          round((l_tmp[0]) / calculator, 2), round((l_tmp[1]) / calculator, 2),
          round((l_tmp[2]) / calculator, 2), round((l_tmp[3]) / calculator, 2),
          round((l_tmp[4]) / calculator, 2), round((l_tmp[5]) / calculator, 2),
          round((l_tmp[6]) / calculator, 2), round((l_tmp[7]) / calculator, 2),
          round((l_tmp[8]) / calculator, 2), round((l_tmp[9]) / calculator, 2),
          round((l_tmp[10]) / calculator, 2))


# 重新划分聚类为0，-1
def DivideCluster(np_cluster):
    new_l_cluster = list()
    for cluster in np_cluster:
        if cluster == 0:
            new_l_cluster.append(0)
        else:
            new_l_cluster.append(1)
    return np.array(new_l_cluster)


def CsvWriter(title, l_type, np_Label, store):
    if store == "default":
        path = "C:/Users/JinCh/PycharmProjects/pythonProject/Steam/project/project_cluster"
        os.chdir(path)
    else:
        pass
    with open("{}_AchievementsDamn.csv".format(title), mode='w', newline='', encoding='UTF-8') as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow(["Steam ID", "last Two Weeks", "ATH", "scoreSum", "status_U_Count",
                           "Level", "Badges", "Games", "Friends", "Groups", "Screenshots", "Reviews", "Cluster"])
        for i in range(len(l_type)):
            user = l_type[i]
            csvWriter.writerow([user.steamId, user.lastTwoWeeks, user.ATH, user.scoreSum, user.status_U_Count,
                                user.level, user.badges, user.games, user.friends, user.groups, user.screenshots,
                                user.reviews, np_Label[i]])
        file.close()


# 计算Ru
def Calculate_Ru(row, weight):
    w1 = 3 * weight  # playtime: 9
    w2 = weight  # pursuit: 3
    w3 = 7 * weight  # social: 21
    Ru = ((row[0] + row[1] + row[2]) / w1) + \
         (row[3] / w2) + \
         ((row[4] + row[5] + row[6] + row[7] + row[8] + row[9] + row[10]) / w3)
    return Ru


def ResultCsvWriter(title, fileLabel, l_type, np_Type, np_Label, store, data):
    if store == "default":
        path = "C:/Users/JinCh/PycharmProjects/pythonProject/Steam/project/project_cluster"
        os.chdir(path)
    else:
        pass
    with open("{}_Achievements{}.csv".format(title, fileLabel), mode='w', newline='', encoding='UTF-8') as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow(["rank", "Steam ID", "last Two Weeks", "ATH", "scoreSum", "status_U_Count",
                           "Level", "Badges", "Games", "Friends", "Groups", "Screenshots", "Reviews", "Cluster", "R"])
        if data == "scaled":
            for i in range(len(l_type)):
                user = l_type[i]
                R = Calculate_Ru(np_Type[i], 3)
                csvWriter.writerow([user.fromRank, user.steamId, np_Type[i][0], np_Type[i][1], np_Type[i][2],
                                    np_Type[i][3], np_Type[i][4], np_Type[i][5], np_Type[i][6], np_Type[i][7],
                                    np_Type[i][8], np_Type[i][9], np_Type[i][10], np_Label[i], R])
        elif data == "original":
            for i in range(len(l_type)):
                user = l_type[i]
                R = Calculate_Ru(np_Type[i], 3)
                csvWriter.writerow([user.fromRank, user.steamId, user.lastTwoWeeks, user.ATH, user.scoreSum,
                                    user.status_U_Count, user.level, user.badges, user.games, user.friends, user.groups,
                                    user.screenshots, user.reviews, np_Label[i], R])
        file.close()


if __name__ == "__main__":
    d_Games = Cluster.GameListReader("gameList.csv")
    l_Total_Users_Cleaned, l_P_Total_Users = Cluster.GameFileReader(d_Games)
    users = np.array(l_P_Total_Users)

    # 数据归一化:
    users_Normalize = Normalize(users)
    """# svd分析:
    component = SVD_Analyze(users_Normalize, threshold=0.90)"""
    component = 3
    # 数据标准化:
    users_Standard = Standard(users)
    # PCA降维，用于聚类:
    users_PCA = PCA_Decomposition(users_Standard, component)
    # 按照3个part进行PCA降维
    users_PCA_new = My_Decomposition(users_Standard)
    """# KPCA降维，用于聚类
    users_KPCA = KPCA_Decomposition(users_Standard, component)"""
    # 聚类
    # PCA1.0 & 4.7%: in TB10 value = 0.38, in total63 value = 0.252
    # PCA2.0 & 4.7%: in TB10 value = , in total63 value = 0.2125
    labels = Dbscan(users_PCA_new, value=0.2125)
    # 重新划分聚类为0，1
    new_labels = DivideCluster(labels)
    # 数可视化：

    # 方差过滤：
    """# LDA降维
    users_LDA = LDA_Discriminant(users_Standard, labels, component)"""

    """# 由聚类结果写入csv文档
    ResultCsvWriter(title="Total", fileLabel="7", l_type=l_Total_Users_Cleaned, np_Type=users_Normalize,
                    np_Label=labels, store="default", data="original")"""

    # print("聚类后的标签为：{}".format(labels))
    # 计算离群数据
    calculate(l_users=l_P_Total_Users, np_cluster=labels, x=0)
    # 画图
    draw3DScatter(data_array=users_PCA_new, clustered_label=new_labels)

    # T-SNE降维
    # Tsne(users_Normalize)
    plt.show()
