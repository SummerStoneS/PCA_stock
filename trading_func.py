# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
from ou_estimation import ou_estimation
from scipy.optimize import minimize


def trading_signal(cum_residuals, last_sign, i):
    """
    :param cum_residuals: 之前T天每只股票的累积残差
    :param last_sign: 之前T天每只股票的股价
    :return: 当天每支股票的交易信号具体值signal，R_square，和买入+1，卖出-1，不持有0的信号方向sign
    """
    open_line = 1.75
    close_line = 0.5
    ou_result = ou_estimation(cum_residuals)

    # 获取最后一天的累积残差
    resid_T = cum_residuals[-1:]
    m = cum_residuals.mean()
    sigma = cum_residuals.std()

    adj_sigma = sigma / np.sqrt(ou_result['k'])
    signal = (resid_T - m) / adj_sigma
    signal = signal.T
    signal.columns = ['s']

    # initialize "sign":buy then 1,short then -1
    sign = pd.Series([0] * len(signal), name='sign', index=signal.index)

    if i != 0:
        sign.update(last_sign)

    sign = pd.concat([sign, ou_result['R_square'], signal], axis=1)

    # 定义交易信号
    open_short = sign['s'] > open_line
    open_long = sign['s'] < -open_line
    close_long = sign['s'] > -close_line
    close_short = sign['s'] < close_line
    current_long = last_sign > 0
    current_short = last_sign < 0

    if i != 0:
        # 如果是第一天，不需要关仓
        sign['sign'][current_long & close_long] = 0
        sign['sign'][current_short & close_short] = 0

    current_zero = sign['sign'] == 0
    sign['sign'][current_zero & open_long] = 1
    sign['sign'][current_zero & open_short] = -1

    # if R_square<0.75, clear position
    sign['sign'][sign['R_square'] < 0.75] = 0

    return sign


def optimize_allocation(sign, loadings, n, unchanged, I_adj = 1):
    """
    :param sign: buy then +1, short then -1
    :param loadings: factor loadings (N,p)
    :param n: 仓位有变化的股票
    :param unchanged: 本期不变的仓位之和，自带做多做空符号
    :param I_adj: I-本期不变的仓位【绝对值】和
    :return: asset allocation of each stock
    """
    # initialize bounds of positions q for n trading stocks,q>0
    bnds = [(0, None)] * n
    # initial values of each position is 0
    x0 = [0] * n

    # 需要最小化的目标函数 target_func(q,L,sign.sign)
    def target_func(q, l, sign):
        target = l.apply(lambda x: abs(np.dot(x, sign * q))).sum()
        return target

    # 套利约束，self-investment
    def constraint_1(q, sign):
        return sum(sign * q) + unchanged

    # leverage约束，I应该使收益波动率最小
    def constraint_2(q):
        return sum(q) - I_adj

    def constraint_3(q, sign):
        return abs((sign == 0)*q).sum()

    cons = ({'type': 'eq', 'fun': constraint_1, 'args': (sign.sign,)},
            {'type': 'eq', 'fun': constraint_2},
            {'type': 'eq', 'fun': constraint_3, 'args': (sign.sign,)})

    res = minimize(target_func, x0, method='SLSQP', bounds=bnds, constraints=cons, args=(loadings, sign.sign))

    return res.x


def optimize_allocation_tf(sign, loadings, n, unchanged, I_adj = 1):
    """
    :param sign: buy then +1, short then -1
    :param loadings: factor loadings (N,p)
    :param n: 仓位有变化的股票
    :param unchanged: 本期不变的仓位之和，自带做多做空符号
    :param I_adj: I-本期不变的仓位【绝对值】和
    :return: asset allocation of each stock
    """
    import tensorflow as tf
    # initialize bounds of positions q for n trading stocks,q>0

    t_l = tf.constant(loadings.T.values)
    t_s = tf.constant(sign.sign.values, dtype=tf.float64)
    t_q = tf.Variable([0] * n, dtype=tf.float64)
    t_q_ = tf.expand_dims(t_q, 1)
    t_s_ = tf.expand_dims(t_s, 1)
    target = tf.reduce_sum(tf.matmul(t_l, t_q_ * t_s_))
    constraint1 = tf.abs(tf.reduce_sum(t_s * t_q) + tf.constant(unchanged, dtype=tf.float64))
    constraint2 = tf.abs(tf.reduce_sum(t_q) - tf.constant(I_adj, dtype=tf.float64))
    constraint3 = tf.reduce_sum(tf.abs(tf.cast(tf.equal(t_s, 0), tf.float64) * t_q))
    constraint4 = tf.reduce_sum(tf.abs(t_q) - t_q)
    constraints = [constraint1, constraint2, constraint3, constraint4]

    loss = target + (constraint1 + constraint2 + constraint3 + constraint4)

    global_step = tf.Variable(0)
    learning_rate = tf.train.exponential_decay(1.0, global_step, 10, 0.95)
    optimizer = tf.train.RMSPropOptimizer(learning_rate)
    train_op = optimizer.minimize(loss, global_step=global_step)
    loss_val = 999
    with tf.Session().as_default() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(2000):
            _, loss_val_, cons = sess.run([train_op, loss, constraints])
            if loss_val - loss_val_ < 1e-4 and max(cons) < 1e-3:
                break
            loss_val = loss_val_
        result = sess.run(t_q)
    assert max(cons) < 1e-3, "Constraints not met %s" % str(cons)
    return result

