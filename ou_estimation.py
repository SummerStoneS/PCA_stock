# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima_model import ARMA
import statsmodels.tsa.stattools as tsa


def get_residual(data_matrix, factors):
    """
    :param data_matrix: (T,N)
    :param factors:  factors (p,T)
    :return: cumulative residual matrix
    """

    price_ret = data_matrix.apply(lambda x: np.log(x)-np.log(x.shift(1)))              #np.log(x).diff()
    price_ret = price_ret.iloc[1:, :]                                                   # 删除第一行
    price_ret = price_ret.fillna(0)

    factors = factors.T
    factors.index = factors.index.to_datetime()
    # F:(t,p)
    factors = factors.ix[price_ret.index]

    # 求载荷矩阵 L   N支股票对p个市场组合
    loadings = []
    residuals = pd.DataFrame()
    stock_name = price_ret.columns

    for i in range(price_ret.shape[1]):
        linreg = LinearRegression()
        model = linreg.fit(factors, price_ret.iloc[:, i])
        loadings.append(model.coef_)
        residual = price_ret.iloc[:, i]-model.predict(factors)
        # residuals (T*N)
        residuals[price_ret.columns[i]] = residual

    # loadings:(N,p)
    L = pd.DataFrame(loadings, index=stock_name)

    # 求累积残差 (T,N)
    cum_residual = residuals.cumsum()

    return cum_residual, L


def ou_estimation(cum_residual):
    SST = cum_residual.var()  # 每支股票累积残差序列的方差
    R_square, k = [], []

    for i in range(cum_residual.shape[1]):
        # plt.plot(XX.iloc[:, i])
        # plt.show()
        # _, p, _, _, _, _ = tsa.adfuller(XX.iloc[:, i])
        # p_values.append(p)
        try:
            arma = ARMA(cum_residual.iloc[:, i], order=(1, 0)).fit(maxiter=100, disp=-1)
        except:
            R_square.append(0.1)
            k.append(0.1)
            continue

        # if i == 10:
        #     with open("params.txt", "a") as f:
        #         f.write(",".join(map(str, list(arma.params))) + "\n")
        a = arma.params[0]
        b = arma.params[1]
        SSE = arma.resid.var()
        R_square.append(1 - SSE / SST[i])
        k.append(-np.log(b) * 252)
        m = a / (1 - b)
        # if i == 10:
        #     with open("params.txt", "a") as f:
        #         f.write(str(m) + "\n")

    # print(np.mean(p_values))
    R_square = pd.Series(R_square, index=cum_residual.columns, name='R_square')
    k = pd.Series(k, index=cum_residual.columns, name='k')
    result = {'R_square': R_square, 'k': k}
    return result





