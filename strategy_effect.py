from multiprocessing.pool import Pool
import pandas as pd
from storage import Storage
import os
from get_factors import get_factors
from portfolio_selection import portfolio_selection
from get_position import get_position
from earnings import earnings
from param_effect import extract_data
from get_stock import get_data, split_data

store_path = os.path.join("data", '2013-06-01')
storage = Storage(store_path)


def random_index(stock):
    """
    :param stock: T*N
    :return: 不重复抽75支股票
    """
    import random
    index_list = random.sample(list(stock.columns),75)
    return index_list


def function(trading_start):
    path = os.path.join("data", trading_start)
    storage.path = path
    # Step 1:
    # 获取股价数据,900多能做空的股票
    stock_matrix, stock_estimation, stock_trade = get_data(trading_start, '生物制药', window=60)
    # stock_matrix = extract_data(storage.load('stock_matrix'))
    # stock_estimation, stock_trade = split_data(stock_matrix, trading_start, window=60)

    # 获取股价数据,所有A股
    # stock_matrix = storage.load('stock_matrix')
    # stock_estimation = storage.load('stock_estimation')
    # stock_trade = storage.load('stock_trade')

    # Step 2:
    # 获取因子矩阵factors
    F, R = get_factors(stock_matrix, p=15)

    # Step 3:
    # 筛选投资组合中的股票，选均值回复快的top_n支股票
    portfolio_index = portfolio_selection(stock_estimation, F, window=60, repeat=10, interval=5, top_n=75)
    # 随机筛选75支股票
    # portfolio_index = random_index(stock_trade)

    # Step 4:
    # 获得交易期每日每支股票的头寸
    position = get_position(portfolio_index, stock_trade, F, window=60, I=1)

    # Step 5:
    # 计算收益
    cum_pnl, sharp, total = earnings(stock_trade, position,epsilon=5e-4, window=60, r=0.04/252)

    return sharp

time_list = ['2013-06-01', '2014-06-01', '2015-06-01', '2016-06-01']
#time_list = ['2008-06-01', '2009-06-01', '2010-06-01', '2011-06-01', '2012-06-01', '2013-06-01', '2014-06-01', '2015-06-01','2016-06-01']
time_year = list(map(lambda x: x[:4], time_list))

if __name__ == '__main__':
    # 四个进程
    pool = Pool(4)
    # 返回一个列表，一年对应一个sharp ratio
    sharp_ratio = pool.map(function, time_list)
    sharp_biology = pd.Series(sharp_ratio, index=time_year)
    sharp_biology.to_csv('sharp_biology.csv', index=True, header=True)
    print(sharp_ratio)

## 崖底碎石图
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# def eig(data_matrix):
#     R_all = data_matrix.fillna(method='ffill').pct_change()
#     R_all = R_all.iloc[1:, :]  # 删除第一行
#     R_all = R_all.fillna(0)
#     C = R_all.corr()  # 1/len(R) * normalized(R).T * R  检验，但对角线不是1
#     eig_value, eig_vectors = np.linalg.eig(C)
#     #eig_vectors=pd.Series(np.real(eig_vectors))
#     return eig_vectors
#
# data_matrix = pd.read_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\stock_matrix_2015-06-02.csv',index_col=0)
# data_matrix2=data_matrix[:214]
# eig_value1=eig(data_matrix)
# eig_value2=eig(data_matrix2)
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
# plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
# plt.figure(figsize=(15,10))
# plt.plot(eig_value1, label='window=428')
# plt.plot(eig_value2, label='window=214')
#
# plt.title('崖底碎石图', fontsize=18)
# plt.xlabel('i (第i大特征值)', fontsize=18)
# plt.ylabel('eigen value', fontsize=18)
# plt.legend()
# plt.show()


