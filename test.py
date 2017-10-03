from multiprocessing.pool import Pool
import pandas as pd
from storage import Storage
import os
from get_factors import get_factors
from portfolio_selection import portfolio_selection
from get_position import get_position
from earnings import earnings
from param_effect import extract_data
import numpy as np


store_path = os.path.join("data", '2013-06-01')
global get_factors, portfolio_selection, get_position, earnings
storage = Storage(store_path)
get_factors = storage.wrapper(keys=["F", "R"])(get_factors)
portfolio_selection = storage.wrapper(keys=["portfolio_index"], fmts=["npy"])(portfolio_selection)
get_position = storage.wrapper(keys=["position"])(get_position)

# 初始化sharp ratio序列用于存放不同参数配置或组合每年的sharp
sharp_ratio = []


def function(trading_start):
    path = os.path.join("data", trading_start)
    storage.path = path
    # Step 1:
    # 获取股价数据,900多能做空的股票
    #stock_matrix = extract_data(storage.load('stock_matrix'))
    #stock_estimation = extract_data(storage.load('stock_estimation'))
    #stock_trade = extract_data(storage.load('stock_trade'))

    # 获取股价数据,所有A股
    stock_matrix = storage.load('stock_matrix')
    stock_estimation = storage.load('stock_estimation')
    stock_trade = storage.load('stock_trade')
    # Step 2:
    # 获取因子矩阵factors
    F, R = get_factors(stock_matrix)

    # Step 3:
    # 筛选投资组合中的股票，选均值回复快的top_n支股票
    #portfolio_index = portfolio_selection(stock_estimation, F)
    random_select = np.random.randint(0,stock_estimation.shape[1],75)
    portfolio_index = stock_estimation[random_select].columns

    # Step 4:
    # 获得交易期每日每支股票的头寸
    #position = get_position(portfolio_index, stock_trade, F)
    position = storage.load('position')
    # Step 5:
    # 计算收益
    cum_pnl, sharp, total = earnings(stock_trade, position)
    print(cum_pnl)
    print(sharp)
    #return sharp

if __name__ == '__main__':
    function('2016-06-01')