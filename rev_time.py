import os
from storage import Storage
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

time_list = ['2008-06-01', '2009-06-01', '2010-06-01', '2011-06-01', '2012-06-01', '2013-06-01', '2014-06-01', '2015-06-01','2016-06-01']
time_year = map(lambda x: x[:4], time_list)


def reversion_time(stock):
    stock[stock > 0] = 1
    stock[stock < 0] = -1
    # mean reversion 实现了多少次
    stock.index = list(range(len(stock)))
    happens = np.floor((stock.diff() != 0).sum()/2)         #交易结束时不是零仓位的不计数
    day_of_buy = stock[stock == 1].index
    diff_day_of_buy = np.diff(day_of_buy)
    new_buy = np.where(diff_day_of_buy != 1)[0]
    if len(new_buy) > 0:
        sum_period = new_buy[0]+1+np.diff(new_buy).sum()
    else:
        sum_period = len(day_of_buy)
    day_of_short = stock[stock == -1].index
    diff_day_of_short = np.diff(day_of_short)
    new_short = np.where(diff_day_of_short != 1)[0]
    if len(new_short)>0:
        sum_period += new_short[0]+1+np.diff(new_short).sum()
    else:
        sum_period += len(day_of_short)

    return sum_period, happens


reversion_periods = []
reversion_freq = []
m_r_t = []

for trading_start in time_list:
    store_path = os.path.join("data", trading_start)
    storage = Storage(store_path)
    position = storage.load('position')

    for stock in position.columns:
        sum_period, happens = reversion_time(position[stock])
        reversion_periods.append(sum_period)
        reversion_freq.append(happens)
    m_r_t.append(sum(reversion_periods)/sum(reversion_freq))

m_r_t = pd.Series(m_r_t, index=time_list)
plt.figure(figsize=(15.0, 10.0))
plt.plot(m_r_t.values, 'r-o')
plt.title('mean reversion time each year', fontsize=18)
plt.xlabel('year', fontsize=18)
plt.ylabel('Realized mean-reversion time(days)', fontsize=18)
plt.xticks(range(9), time_year)
plt.ylim(8, 18)

plt.show()
mean_reversion_time = sum(reversion_periods)/sum(reversion_freq)
print(m_r_t)
#print(mean_reversion_time, sum(reversion_periods), sum(reversion_freq))