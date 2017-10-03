# -*- coding: utf-8 -*-
from get_stock import get_data
from get_factors import get_factors
from portfolio_selection import portfolio_selection
from get_position import get_position
from earnings import earnings
import pandas as pd
import numpy as np
from storage import Storage
import os
from param_effect import extract_data

store_path = os.path.join("data", '2013-06-01')
global get_data, get_factors, portfolio_selection, get_position, earnings
storage = Storage(store_path)
get_data = storage.wrapper(keys=["stock_matrix", "stock_estimation", "stock_trade"])(get_data)
get_factors = storage.wrapper(keys=["F", "R"])(get_factors)
portfolio_selection = storage.wrapper(keys=["portfolio_index"], fmts=["npy"])(portfolio_selection)
get_position = storage.wrapper(keys=["position"])(get_position)
# earnings = storage.wrapper(keys=["cum_pnl"])(earnings)


def run_main(trading_start):

    window = 60
    top_n = 75
    p = 15
    repeat = 5
    path = os.path.join("data", trading_start)
    # if not os.path.exists(path):
    #     # 创建文件夹 叫path
    #     os.mkdir(path)
    storage.path = path

    interval = 5
    industry = ''
    I = 1
    r = 0.04/252

    # Step 1:
    # 获取指定交易日期和行业的股价数据，默认是所有
    # stock_matrix, stock_estimation, stock_trade = get_data(trading_start, industry, window)
    # stock_matrix = pd.read_csv('./data/stock_matrix2014-06-01.csv', index_col=0, parse_dates=True)
    # stock_matrix = storage.load('stock_matrix')
    # stock_estimation = storage.load('stock_estimation')
    # stock_trade = storage.load('stock_trade')

    stock_matrix = extract_data(storage.load('stock_matrix'))
    stock_estimation = extract_data(storage.load('stock_estimation'))
    stock_trade = extract_data(storage.load('stock_trade'))
    # Step 2:
    # 获取因子矩阵factors
    F, R = get_factors(stock_matrix, p)
    # stock_estimation = pd.read_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\stock_estimation2014-06-01.csv',index_col=0,parse_dates=True)
    #F = pd.read_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\F.csv', index_col=0, parse_dates=True)

    # stock_estimation = storage.load("stock_estimation")
    # F = storage.load('F')

    # Step 3:
    # 筛选投资组合中的股票，选均值回复快的top_n支股票
    portfolio_index = portfolio_selection(stock_estimation, F, window, repeat, interval, top_n)
    # portfolio_index = np.load('./portfolio_index.npy')
    # stock_trade = pd.read_csv('./data/stock_trade2014-06-01.csv', index_col=0, parse_dates=True)
    #stock_trade = storage.load('stock_trade')

    # Step 4:
    # 获得交易期每日每支股票的头寸
    position = get_position(portfolio_index, stock_trade, F, window, I)
    # position = pd.read_csv('./data/2014-06-01/position.csv', index_col=0, parse_dates=True)
    # position = storage.load('position')
    # 获得收益
    cum_pnl, sharp_total, total = earnings(stock_trade, position)
    #cum_pnl.to_csv('C:\\Users\\ThinkPad\\OneDrive\\outcomes\\cum_pnl2016.csv',index=True)
    print(sharp_total)
    return(sharp_total)


if __name__ == '__main__':
    time_list = ['2013-06-01', '2014-06-01', '2015-06-01', '2016-06-01']
    sharp_all = []
    for i in time_list:
        sharp = run_main(i)
        sharp_all.append(sharp)
    print(sharp_all)







