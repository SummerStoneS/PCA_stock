# Background
Pairs trading is very popular among statistical arbitrage. But pairs trading is known to be exposed to spread risk and horizon risk. In recent years, O-U process is found to be efficient in the arbitrage process for its ability in describing the mean-reversion process. This project uses the coefficient of the O-U process to filter the stocks that have fastest mean-reversion rates into the investment portfolio beforehand, and calculate the average mean-reversion cycle in transaction periods. 

The principal component analysis method is used to create matched pairs and then implement generalized pairs trading. First, use principal component analysis to all stocks, select the most important 15 components, and then use multiple linear regression and least squares to estimate factors’ coefficients, then fit resulting residual sequence with O-U process. According to the results of O-U fitting, we choose stocks with fastest mean-reversion speeds to construct the portfolio. In the trading period, I establish the arbitrage interval according to the degree of residual deviation. Finally, strategy_effect.py studies the effect of parameter.

The empirical data involves March 2008 - March 2017 China's A-share stocks. After taking into account the transaction costs and margin costs the profits are positive. Then I narrow the scope of the stocks to the 950 of the latest short able stocks, the proceeds slightly reduced. 


# Introduction of each .py
## get_stock.py
  - `get_industry()`
    returns all stocks code with their industry labels
  - `get_list(industry='')`
    returns list of stock codes that match the industry you give
  - `get_stock(start_d, end_d, stock_list)`
    returns T*N stock price matrix given the start date, end date and stock codes you give
  - `get_data(trading_start, industry='', window=60)`
    returns estimation_data and trading data, estimation_data is for selecting stocks that are most stable and fast mean-reverted. trading data is for trading the stocks that previously stand out.
    
## get_factors.py
This function implements principal component analysis to the basket of stocks in the stock selection period.
params p is the number of component you want to have in the analysis. note that p is not the larger the better. when p becomes too large, the noise becomes siginificant, too. so follow the scree  plot should be a good choice.

the process of PCA should involve key steps as shown bellowed:
1. change the stock price to return
2. calculate correlation matrix(C) of stock return
3. calculate eigen value and eigen vectors of C 
4. sort eigen values, and select top p eigen vectors that have the p largest eigen values
5. adjust eigen values by stock volatility
6. calculate p factors
This function returns p factors, each factor is a linear combination of the initial N stocks, the coefficients are derived from (5)  

## ou_estimation.py
I use O-U stochastic process to fit the residual of each stock, which means each stock return subtracts the common p factors
  - `get_residual(data_matrix, factors)`
    this function runs a multi-linear regression on the stock returns and the p factors, and it returns residuals and loading factors.
  - `ou_estimation(cum_residual)`
    this function returns the parameters of ou-estimation on each stock. parameter k measures the mean-reversion speed. R-square is an indication of robustness. Note that the discrete version of ou-estimation, which is a continious time series model, is an ARMA(1,0) model.
    
## portfolio_selection.py
`portfolio_selection(stock_estimation, factors, window=60, repeat=10, interval=5, top_n=75)`
    :param stock_estimation: estimation data
    
    :param window: estimation window 30,60,90,120
    
    :param repeat: estimation times
    
    :param interval: moving window interval
    
    :param top_n: number of stocks to be selected into portfolio
    
    :return: indices of stocks in the portfolio, type = list
   this fuction returns the 75 stocks codes list that have the fastest mean-conversion rate, and should be traded in the next level.

## get_position.py
`get_position(portfolio_index, stock_trade, factors, window=60, I=1)`
This function returns the positions of each stocks in the whole trading periods.
This should involve two steps:
1. calculate the trading signal of each stock
2. allocate funds on each stock that has a trading signal, whether long or short

## trading_func.py
This .py supports the process in the above get_position.py
`trading_signal(cum_residuals, last_sign, i)`
This fuction actually calculates the trading signal of each stock. when the sum_of_residuals of T-days before deviates too much, it generates a signal for long or short that tock.
`optimize_allocation(sign, loadings, n, unchanged, I_adj = 1)`
This function realize asset allocation of each stock with `scipy.optimize.minimize`

## earnings.py
This function returns the total p&l and sharpe ratio of this trading strategy.

## visualize.py
This function visulizes the total pnl, max_drawdown, scree plot and a regression of strategy return on hs300

## strategy_effect.py & params_effect.py
These two .py study the effect of params in the overall strategy
