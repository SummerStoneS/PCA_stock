import pandas as pd
import numpy as np
import tushare as ts


def earnings(stock_trade, position, epsilon=5e-4, window=60, r=0.04/252):
    """
    :param position: T,N
    :param window:
    :param I: leverage
    :param r: risk free rate daily
    :param epsilon: 手续费 5bps
    :return:
    """
    # 用最近的值填充停牌期的价格，计算收益率时此停牌期收益率为零

    stock_data = stock_trade[window:]
    stock_data = stock_data.loc[:, stock_data.columns.isin(position.columns)]

    ret = stock_data.fillna(method='ffill').pct_change().iloc[1:, :].fillna(0)

    # 投资组合的每日资本利得
    # 单边做多
    # hs300 = ts.get_k_data('000300',start=stock_data.index[0],end=stock_data.index[-1], index=True)[['date', 'close']]
    # hs300.index = hs300['date']
    # del hs300['date']
    # hs300 = hs300.fillna(method='ffill').pct_change().iloc[1:, :].fillna(0)
    # ret = ret.sub(hs300.iloc[:, 0], axis=0)
    # position[position < 0] = 0
    borrow_rate = 0.0836 / 360
    cum_pnl = [1]
    wealth = 1                                  # 初始财富1

    # 投资收益
    invest_return = wealth*pd.DataFrame(position.values[:-1] * ret.values, index=ret.index, columns=ret.columns).sum(axis=1)
    # 投资成本 如果是自有资金的话，可以在最后算机会成本
    invest_cost = r * position.sum(axis=1).values[:-1]
    # 交易手续费
    transaction_cost = abs(position.diff()).sum(axis=1).values[1:] * epsilon
    # 融券费用
    borrow_cost = abs(position[position < 0]).sum(axis=1).values[:-1] * borrow_rate
    total = invest_return - invest_cost - transaction_cost - borrow_cost
    #total = invest_return - transaction_cost - borrow_cost
    for i in range(len(position) - 1):
        wealth += wealth * total[i]
        cum_pnl.append(wealth)

    cum_pnl = pd.Series(cum_pnl, index=position.index)
    # cum_pnl.to_csv('./data/cum_pnl.csv', index=True)

    sharp_invest = (invest_return.mean())/invest_return.std()*np.sqrt(252)
    # ret_total = cum_pnl.diff()
    ret_total = cum_pnl.pct_change().dropna()
    sharp_total = ((ret_total.mean())-r) / ret_total.std() * np.sqrt(252)

    # invest_return.to_csv('./data/invest_return.csv', index=True)
    # np.save('./data/invest_cost.npy', invest_cost)
    # np.save('./data/transaction_cost.npy', transaction_cost)
    # np.save('./data/total.npy', total)
    # ret_total.to_csv('./data/ret_total.csv', index=True)

    return cum_pnl, sharp_total, total
