import pandas as pd
import numpy as np
from trading_func import trading_signal, optimize_allocation
from ou_estimation import get_residual


def get_position(portfolio_index, stock_trade, factors, window=60, I=1):
    """
    :param window:
    :param p:
    :param I: leverage ,should be set to minimize volatility of returns
    :return: (T,N)DataFrame of positions each day in trading periods with buy/short sign
    """
    # portfolio_stock_data dim(T,top_n)
    stock_data = stock_trade.loc[:, stock_trade.columns.isin(list(portfolio_index))]
    # cum_residual: (T,N),loadings: (N,p)

    cum_residual_all, loadings = get_residual(stock_data, factors)

    position = pd.DataFrame()
    sign_before = pd.DataFrame({"sign": [0] * len(stock_data.columns)}, index=stock_data.columns)

    for i in range(len(stock_data) - window):

        cum_residuals = cum_residual_all[:window+i]
        # 每天用之前T天的数据做OU拟合，用前一天的数据得到下一天的交易信号，并计算相应仓位
        # trade_data = stock_data[i:i+window]

        # sign:buy/short,R_square:robust,signal:具体的偏离程度计量
        sign = trading_signal(cum_residuals, sign_before.sign, i)

        n = len(sign)

        # 找出缺失的股票,在优化的时候去掉这些股票，I减去这些股票的仓位
        if i == 0:
            sign_before = sign
            sign_before['q'] = [0]*n
        if ((sign.sign >= 0).all() or (sign.sign <= 0).all()) and not (sign.sign == 0).all():
            pass
        elif (sign.sign == 0).all():
            sign_before.q = 0
        else:
            not_found = sign_before[~sign_before.index.isin(sign.index)]
            unchanged = np.dot(not_found.sign, not_found.q)
            I_adj = I - not_found.q.sum()

            # 计算本期参与优化的股票的仓位

            q = optimize_allocation(sign, loadings, n, unchanged, I_adj)
            sign['q'] = q
            # 仓位不变的股票这期仓位为上一期的仓位
            sign_before = pd.concat([sign, not_found])
        # position = pd.concat([position, sign_before.q*sign_before.sign], axis=1)
        position[stock_data.index[i + window]] = sign_before.q * sign_before.sign
        print(i)

    position = position.T.sort_index()
    # position.to_csv('./position.csv', index=True)
    return position
