# -*- coding: utf-8 -*-

from get_factors import get_factors
from portfolio_selection import portfolio_selection
from get_position import get_position
from earnings import earnings
import pandas as pd
from functools import partial
#from visualize import visualize,calculate_beta
from multiprocessing.pool import Pool
from storage import Storage
import os
import matplotlib.pyplot as plt
from get_stock import split_data

store_path = os.path.join("data", '2013-06-01')
storage = Storage(store_path)


# 从全A股数据中筛选出融券标的股
def extract_data(dataframe):
    # 读取2016年12月公布的最新融券标的，共950支
    short_code = pd.read_excel('2016.12.2short_index.xlsx', index_col=0)
    # code补零
    short_code.index = map(lambda x: "{:0>6}".format(str(x)), short_code.index)

    dataframe = dataframe.loc[:, short_code.index]
    # 删除没找到的
    dataframe = dataframe.loc[:, ~(dataframe.isnull().sum() == len(dataframe))]
    return dataframe


def com_pare(window=60, top_n=75, p=15, repeat=5, interval=5):
    I = 1
    r = 0.04 / 252
    epsilon = 5e-4

    complete_pnl = pd.DataFrame()
    sharp_ratio = []
    total_return = pd.Series()

    time_list = ['2013-06-01', '2014-06-01', '2015-06-01', '2016-06-01']

    for trading_start in time_list:
        # 定位到指定文件夹
        path = os.path.join("data", trading_start)
        storage.path = path
        # Step 1:
        # 获取股价数据
        stock_matrix = extract_data(storage.load('stock_matrix'))
        stock_estimation, stock_trade = split_data(stock_matrix, trading_start, window)

        # Step 2:
        # 获取因子矩阵factors
        F, R = get_factors(stock_matrix, p)

        # Step 3:
        # 筛选投资组合中的股票，选均值回复快的top_n支股票
        portfolio_index = portfolio_selection(stock_estimation, F, window, repeat, interval, top_n)

        # Step 4:
        # 获得交易期每日每支股票的头寸
        position = get_position(portfolio_index, stock_trade, F, window, I)

        # Step 5:
        # 计算收益
        cum_pnl, sharp, total = earnings(stock_trade, position, epsilon, window, r)
        total_return = pd.concat([total_return, total])
        sharp_ratio.append(sharp)
        cum_pnl = pd.DataFrame(cum_pnl, columns=[trading_start])
        complete_pnl = pd.merge(complete_pnl, cum_pnl, how='outer', left_index=True, right_index=True)
        # 临时保存用
        # save1 = os.path.join(path, 'total_return.csv')
        # save2 = os.path.join(path, 'complete_pnl.csv')
        # total_return.to_csv(save1, index=True, header=True)
        # complete_pnl.to_csv(save1, index=True, header=True)

    return sharp_ratio


def function(w):
    sharp = pd.Series(com_pare(window=60, top_n=w, p=15, repeat=5, interval=5), index=time_year, name=w)
    return sharp
# # 每年累积收益作图
# visualize(complete_pnl)
# 计算相对沪深300指数的beta
#calculate_beta(total_return)

#print(sharp_ratio)
# 绘制变量控制后的比较图，只看2013-2016四年数据
time_list = ['2013-06-01', '2014-06-01', '2015-06-01', '2016-06-01']
time_year = list(map(lambda x: x[:4], time_list))

if __name__ == '__main__':
    #sharp = com_pare(window=60, top_n=50, p=20, repeat=5, interval=5)
    #print(sharp)
    # 初始化
    compare_sharp_factor = pd.DataFrame()
    # 四个进程
    pool = Pool(4)
    sharp_ratios = pool.map(function, [15,20,25,50,75])
    compare_sharp_size = pd.DataFrame(dict(zip([15,20,25,50,75], sharp_ratios)), index=time_year)
    compare_sharp_size.to_csv('compare_sharp_size.csv', index=True, header=True)

    # for top in [15, 20, 25, 50]:
    #     sharp_ratio = com_pare(window=60, top_n=top, p=15, repeat=5, interval=5)
    #     compare_sharp_ratio[top] = pd.Series(sharp_ratio, index=time_year, name=top)
    ## 作图
    # plt.figure(figsize=(15.0, 10.0))
    # plt.plot(compare_sharp_factor)
    # plt.xlabel('time_year)', fontsize=18)
    # plt.ylabel('sharp ratio', fontsize=18)
    # plt.title('Influence of factor number', fontsize=18)
    # plt.xticks(range(4), time_year)
    # plt.show()