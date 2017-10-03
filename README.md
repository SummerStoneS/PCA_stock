## Background
Pairs trading is very popular among statistical arbitrage. But pairs trading is known to be exposed to spread risk and horizon risk. In recent years, O-U process is found to be efficient in the arbitrage process for its ability in describing the mean-reversion process. This project uses the coefficient of the O-U process to filter the stocks that have fastest mean-reversion rates into the investment portfolio beforehand, and calculate the average mean-reversion cycle in transaction periods. 

The principal component analysis method is used to create matched pairs and then implement generalized pairs trading. First, use principal component analysis to all stocks, select the most important 75 components, and then use multiple linear regression and least squares to estimate factors’ coefficients, then fit resulting residual sequence with O-U process. According to the results of O-U fitting, we choose stocks with fastest mean-reversion speeds to construct the portfolio. In the trading period, I establish the arbitrage interval according to the degree of residual deviation. Finally, strategy_effect.py studies the effect of parameter.

The empirical data involves March 2008 - March 2017 China's A-share stocks. After taking into account the transaction costs and margin costs the profits are positive. Then I narrow the scope of the stocks to the 950 of the latest short able stocks, the proceeds slightly reduced. 


## Introduction of each .py
# get_stock.py
  - get_industry()
    returns all stocks code with their industry labels
  - get_list(industry='')
    returns 


Add new line
