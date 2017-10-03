# -*- coding:utf-8 -*-

import pandas as pd
from ou_estimation import ou_estimation, get_residual
import numpy as np


def portfolio_selection(stock_estimation, factors, window=60, repeat=10, interval=5, top_n=75):
    """
    :param stock_estimation: estimation data
    :param window: estimation window 30,60,90,120
    :param repeat: estimation times
    :param interval: moving window interval
    :param top_n: number of stocks to be selected into portfolio
    :return: indices of stocks in the portfolio, type = list
    """

    # 选择进入portfolio的股票
    # 计算每支股票的m次OU过程拟合的k

    k = pd.DataFrame()
    r_2 = pd.DataFrame()
    ix_end = stock_estimation.shape[0]                # 从trading_start date的前一天开始倒退60天估计
    for i in range(repeat):
        # 获取进行一次estimation的数据
        if ix_end-window < 0:
            break
        data_matrix = stock_estimation[ix_end-window-1:ix_end]
        trim_condition = data_matrix.isnull().mean() < 0.5
        data_matrix = data_matrix[trim_condition[trim_condition].index]

        cum_residual, loadings = get_residual(data_matrix, factors)


        # 得到第i次 OU 估计的股票 vs. k 序列
        result = ou_estimation(cum_residual)
        k['k_%d' % i] = result['k']            # 按index内连接每一期每支股票的k值
        r_2[i] = result['R_square']
        ix_end -= interval
    k = k[r_2.mean(axis=1) > 0.75]
    portfolio_index = k.mean(axis=1).sort_values(ascending=False)[:top_n].index

    return portfolio_index





