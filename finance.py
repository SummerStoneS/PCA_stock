# -*- coding: utf-8 -*-
from get_stock import get_data
from get_factors import get_factors
from portfolio_selection import portfolio_selection
from get_position import get_position
from earnings import earnings
import pandas as pd
import numpy as np
import os


def run_main(trading_start):

    window = 60
    top_n = 50
    p = 15
    repeat = 5
    path = os.path.join("data", trading_start)

    interval = 5
    industry = '生物制药'
    I = 1
    r = 0.04/252

    # Step 1:
    # 获取指定交易日期和行业的股价数据，默认是所有
    stock_matrix, stock_estimation, stock_trade = get_data(trading_start, industry, window)
    stock_matrix.to_csv(os.path.join(path, 'bio_all.csv'), index=True, parse_dates=True)
    stock_estimation.to_csv(os.path.join(path, 'bio_estimation.csv'), index=True, parse_dates=True)
    stock_trade.to_csv(os.path.join(path, 'bio_trade.csv'), index=True, parse_dates=True)
    # Step 2:
    # 获取因子矩阵factors
    F, R = get_factors(stock_matrix, p)

    # Step 3:
    # 筛选投资组合中的股票，选均值回复快的top_n支股票
    portfolio_index = portfolio_selection(stock_estimation, F, window, repeat, interval, top_n)

    # Step 4:
    # 获得交易期每日每支股票的头寸
    position = get_position(portfolio_index, stock_trade, F, window, I)
    stock_trade.to_csv(os.path.join(path, 'bio_position.csv'), index=True, parse_dates=True)

    # 获得收益
    cum_pnl, sharp_total, total = earnings(stock_trade, position)
    #cum_pnl.to_csv('C:\\Users\\ThinkPad\\OneDrive\\outcomes\\cum_pnl2016.csv',index=True)
    print(sharp_total)


if __name__ == '__main__':
    time_list = ['2013-06-01', '2014-06-01', '2015-06-01', '2016-06-01']
    for i in time_list:
        run_main(i)