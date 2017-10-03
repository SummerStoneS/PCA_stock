import pandas as pd
import numpy as np
import math


def get_factors(data_matrix, p=15):
    """
    :param data_matrix: T period stock prices for N stocks, index = date, columns = stock_code
    :param p: Number of factors
    :return: cumulative residual matrix
    """
    # 转成收益率序列,目前是（T，N）矩阵
    # method 1
    # data_matrix = data_matrix.pct_change()

    # method 2
    R_all = data_matrix.fillna(method='ffill').pct_change()
    # R = data_matrix.apply(lambda x: np.log(x)-np.log(x.shift(1)))              #np.log(x).diff()
    R_all = R_all.iloc[1:, :]                                                           # 删除第一行
    R_all = R_all.fillna(0)
    # R = R.loc[:, ~R.isnull().any(0)]                                            # 删除有缺失值的列
    # 传入的data因为是两年的，仅使用历史数据求factor，所以只使用前1/2的数据
    R = R_all[:math.floor(len(R_all)*0.5)]
    # 相关系数矩阵
    C = R.corr()                                                                #   1/len(R) * normalized(R).T * R  检验，但对角线不是1
    # 求特征根，特征向量
    eig_value, eig_vectors = np.linalg.eig(C)
    # 取实部，虚数几乎全部为零，少数几个为e^-16量级
    eig_vectors = np.real(eig_vectors)

    # 特征值和特征向量一一对应，默认结果就是从大到小排序
    eig_vectors_df = pd.DataFrame(eig_vectors)
    eig_vectors_df.index = np.real(eig_value)
    eig_vectors_df.columns = C.columns
    eig_vectors_df = eig_vectors_df.sort_index(ascending=False)
    # 取前p个特征值，最大的p个作为factors
    vec = eig_vectors_df.iloc[:p]
    # 计算N支股票的波动率
    sigma = R.std()
    # 计算Q，调整的投资权重
    Q = vec/np.array(sigma)

    # TODO: fill with mean
    # 因子矩阵 factors    (p,T）维
    F = np.dot(Q, R_all.T)
    F = pd.DataFrame(F, columns=R_all.index)

    # F.to_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\F2.csv')
    # R.to_csv('D:\OneDrive\研究生活动\毕业论文\\thesis_code\\data\\R.csv')
    return F, R


