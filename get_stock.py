import tushare as ts
import pandas as pd
import datetime
from datetime import timedelta
import numpy as np


def get_industry():
    all_stock = ts.get_industry_classified()    # 获取所有行业分类的股票
    all_stock.to_csv('all_stock.csv', encoding='gbk', index=False)
    print(all_stock['c_name'].unique())                # 所有行业分类列表


def get_list(industry=''):
    all_stock = pd.read_csv('all_stock.csv', encoding='gbk', dtype=str)
    if industry != '':
        stock_list = all_stock[all_stock['c_name'] == industry]['code']  # 获取行业内所有股票的code
    else:
        stock_list = all_stock.code
    return stock_list


def get_stock(start_d, end_d, stock_list):
    """
    :param start_d: str   start date of captured stock data
    :param end_d:   str   end date of captured stock data
    :param stock_list: list   stock code to be captured
    :return: T*N stock price matrix
    """
    stock_matrix = {}
    stock_matrix = pd.DataFrame(stock_matrix)
    for stock_name in stock_list:
        try:
            new_stock = ts.get_k_data(stock_name, start=start_d, end=end_d)[['date', 'close']]
        except:
            continue
        new_stock.index = new_stock['date']
        del new_stock['date']
        new_stock.columns = ['%s' % stock_name]
        stock_matrix = pd.concat([stock_matrix, new_stock], axis=1)

    # 删除列缺失数据,余下的股票在日期内都有数据
    # stock_matrix = stock_matrix.dropna(axis=1)
    # 缺失值比例比例小于0.3
    trim_condition = stock_matrix.isnull().mean() < 0.3
    stock_matrix = stock_matrix[trim_condition[trim_condition].index]
    # save_name = 'stock_matrix_'+start_d+'.csv'
    # stock_matrix.to_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\%s' % save_name)
    return stock_matrix


def split_data(stock_matrix, trading_start, window):
    trading_start_dt = datetime.datetime.strptime(trading_start, '%Y-%m-%d')
    # 找到交易日所在行
    stock_matrix.index = stock_matrix.index.to_datetime()
    while not (stock_matrix.index == trading_start_dt).any():
        trading_start_dt += timedelta(days=1)
    line = np.where(stock_matrix.index == trading_start_dt)[0][0]

    # 截取estimation期数据
    stock_estimation = stock_matrix[:line]
    # 截取trade期数据
    stock_trade = stock_matrix[line-window:]
    return stock_estimation, stock_trade


def get_data(trading_start, industry='', window=60):
    """
    :param trading_start: 交易开始的日期
    :param industry: 默认取所有，字符串，如‘金融行业’
    :param window: 滚动窗的长度
    :return: estimation和trade期的数据
    """
    trading_start_dt = datetime.datetime.strptime(trading_start, '%Y-%m-%d')

    estimation_start_dt = trading_start_dt-datetime.timedelta(365)
    estimation_start = datetime.datetime.strftime(estimation_start_dt, '%Y-%m-%d')

    trading_end_dt = trading_start_dt + datetime.timedelta(365)
    trading_end = datetime.datetime.strftime(trading_end_dt, '%Y-%m-%d')

    stock_list = get_list(industry)  # 获取行业内所有股票的code

    # estimation和trade期的所有数据，两年
    stock_matrix = get_stock(estimation_start, trading_end, stock_list)

    stock_estimation, stock_trade = split_data(stock_matrix, trading_start,window)

    # path1 = 'stock_estimation' + trading_start + '.csv'
    # path1 = "D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\stock_estimation_%s.csv" % trading_start
    # path2 = 'stock_trade' + trading_start + '.csv'
    # path3 = 'stock_matrix' + trading_start + '.csv'

    # stock_estimation.to_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\%s' % path1)
    # stock_trade.to_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\%s' % path2)
    # stock_matrix.to_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\%s' % path3)

    return stock_matrix, stock_estimation, stock_trade

