import os
from storage import Storage
import pandas as pd
import matplotlib.pyplot as plt
from earnings import earnings
import tushare as ts
from scipy import stats
import numpy as np
from param_effect import extract_data


#time_list = ['2008-06-01', '2009-06-01', '2010-06-01', '2011-06-01', '2012-06-01', '2013-06-01', '2014-06-01', '2015-06-01','2016-06-01']
time_list = ['2013-06-01', '2014-06-01', '2015-06-01', '2016-06-01']
store_path = os.path.join("data", '2013-06-01')
storage = Storage(store_path)


def get_cum_pnl():
    complete_pnl = pd.DataFrame()
    sharp_ratio = []
    epsilon = 5e-4
    total_return = pd.Series()
    for trading_start in time_list:
        path = os.path.join("data", trading_start)
        storage.path = path
        # 全A股
        stock_trade = storage.load('stock_trade')
        # 900支
        # stock_trade = extract_data(storage.load('stock_trade'))
        position = storage.load('position')
        cum_pnl, sharp, total = earnings(stock_trade, position, epsilon)

        total_return = pd.concat([total_return, total])
        sharp_ratio.append(sharp)
        cum_pnl = pd.DataFrame(cum_pnl, columns=[trading_start])
        complete_pnl = pd.merge(complete_pnl, cum_pnl, how='outer', left_index=True, right_index=True)

    total_return.to_csv('total_return.csv', index=True, header=True)
    print(sharp_ratio)
    #
    save_path = 'complete_pnl.csv'
    complete_pnl.to_csv(save_path, index=True)


def visualize(complete_pnl):
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
    plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

    plt.figure(figsize=(15.0, 10.0))
    plt.plot(complete_pnl)
    plt.xlabel('time(year)', fontsize=18)
    plt.ylabel('cumulative PnL', fontsize=18)
    plt.title('controlled portfolio,手续费=5bp', fontsize=18)
    plt.show()
    # plt.savefig('fig5ps.png')


def calculate_beta(total_return):
    total_return = total_return.diff().dropna()
    hs300 = ts.get_k_data('000300', start='2013-06-04', end='2017-03-03', index=True)[['date', 'close']]
    hs300.index = hs300['date']
    del hs300['date']
    hs300_ret = hs300.pct_change()[1:]
    hs300_ret.index = hs300_ret.index.to_datetime()
    hs300_ret = hs300_ret.ix[total_return.index, :].dropna()
    total_return = total_return.ix[hs300_ret.index, :]
    slope, intercept, r_value, p_value, std_err = stats.linregress(hs300_ret.values.flat, np.array(total_return).flat)
    print(slope, intercept, r_value, p_value, std_err)
    beta = pd.concat([hs300_ret, total_return], axis=1)
    beta.to_csv('C:\\Users\\ThinkPad\\OneDrive\\outcomes\\beta_900.csv', index=True)


def max_drawdown(complete_pnl):
    index_2013 = slice('2013-06-03', '2014-05-30')
    index_2014 = slice('2014-06-04', '2015-06-01')
    index_2015 = slice('2015-06-02', '2016-05-31')
    index_2016 = slice('2016-06-02', '2017-03-03')
    index_list = [index_2013, index_2014, index_2015, index_2016]
    max_dd = []
    time_list2 = ['2013/6/1', '2014/6/1', '2015/6/1', '2016/6/1']
    for i in range(len(time_list)):
        col = index_list[i]
        cum_pnl = complete_pnl.ix[col, time_list2[i]]
        mdd = (cum_pnl.cummax()-cum_pnl).max()              # 计算最大回撤
        max_dd.append(mdd)
        #plt.plot(cum_pnl)
        #plt.plot(cum_pnl.cummax())
        ret_total = cum_pnl.pct_change().dropna()
        sharp_total = ((ret_total.mean()) - 0.04/252) / ret_total.std() * np.sqrt(252)
        print(sharp_total)
    max_dd = pd.Series(max_dd, index=time_list)
    max_dd.to_csv('C:\\Users\ThinkPad\OneDrive\outcomes\\2000\\mdd.csv', index=True)


if __name__ == '__main__':
    #get_cum_pnl()
    read_path = 'C:\\Users\\ThinkPad\\OneDrive\\outcomes\\complete_pnl.csv'
    complete_pnl = pd.read_csv(read_path, index_col=0, parse_dates=True)
    # total_return = pd.read_csv(read_path, index_col=0, parse_dates=True)
    # visualize(complete_pnl)
    #calculate_beta(total_return)
    max_drawdown(complete_pnl)