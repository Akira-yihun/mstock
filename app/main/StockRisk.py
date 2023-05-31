import pandas as pd
import numpy as np
import math
from scipy.optimize import minimize

def stat_return_ratio(df):
    '''
    count return ratio in intervals\n
    return dataframe\n
    +--------+------+-----------+\n
    |interval|counts|possibility|\n
    +--------+------+-----------+
    '''
    rate = df['rate'][1:]
    lrate = math.ceil(min(rate)*100-1)/100
    rrate = math.floor(max(rate)*100+1)/100
    a = min([lrate, -0.1])
    b = max([rrate, 0.1])
    rate = np.array(rate)
    #sep = [a]
    #mid = [i/100 for i in range(-9, 10, 1)]
    #sep.extend(mid)
    #sep.append(b)
    sep = [i/100 for i in range(int(a*100)-1, int(b*100)+1, 1)]
    s = pd.cut(rate, sep, right = False)
    sc = s.value_counts()
    sc = pd.DataFrame(sc)
    sc['possibility'] = sc['count']/sum(sc['count'])
    sc['left'] = sep[:-1]
    sc['right'] = sep[1:]
    return sc


def get_utility(x):
    if x >= 0:
        return math.log(1+abs(x))
    else:
        return -math.log(1+abs(x))


def get_item_of_one(df, stockid, stockname):
    '''
    EUE: Expected Utility-Entropy Model\n
    NEUE: Normalized Expected Utility-Entropy Model\n
    EUEV: Expected Utility-Entropy-Variance\n
    EUEVS: Expected Utility-Entropy-Variance-Skewness Model\n
    return stockstat\n
    {entropy, utility, variance, skewness, s_entropy}
    '''
    statr = stat_return_ratio(df)
    entropy = 0
    utility = 0
    for row in statr.itertuples():
        mr = (getattr(row, 'left')+getattr(row, 'right'))/2
        p = getattr(row, 'possibility')
        if p != 0:
            entropy += -p * math.log(p)
            utility += p * get_utility(mr)
    rate = df['rate'][1:]
    stockstat = {}
    stockstat['stockid'] = stockid
    stockstat['stockname'] = stockname
    stockstat['entropy'] = entropy
    stockstat['utility'] = utility
    stockstat['variance'] = rate.var()
    stockstat['skewness'] = rate.skew()
    stockstat['s_entropy'] = entropy/math.log(len(rate))
    return stockstat


def get_items(df):
    maxuti = max([abs(df['utility'].min()),abs(df['utility'].max())])
    maxvar = df['variance'].max()
    maxske = max([abs(df['skewness'].min()),abs(df['skewness'].max())])
    if maxuti == 0:
        df['s_utility'] = 0
    else:
        df['s_utility'] = df['utility']/maxuti
    if maxvar == 0:
        df['s_variance'] = 0
    else:
        df['s_variance'] = df['variance']/maxvar
    if maxske == 0:
        df['skewness'] = 0
    else:
        df['s_skewness'] = df['skewness']/maxske
    df['e_v'] = (df['s_entropy'] + df['s_variance'])/2
    df['e_v_s'] = (df['s_entropy'] + df['s_variance'] - df['s_skewness'])/3
    return df

def std(cordf):
    def inner(weights):
        weights = np.array(weights)
        return np.sqrt(np.dot(np.dot(weights, np.array(cordf.cov())), weights.T))
    return inner

import matplotlib.pyplot as plt


def efficient_frontier(ratedf):
    thisstd = std(ratedf)
    mean_r = ratedf.mean()
    x_init = [1/len(mean_r) for i in range(len(mean_r))]
    resweightslis = []
    resstdlis = []
    lrate = mean_r.max()
    rrate = mean_r.min()
    for r in np.linspace(lrate, rrate, 100):
        constraint = (
            {'type': 'eq', 'fun': lambda x: np.sum(x)-1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, mean_r)-r},
        )
        bound = [(0,1) for i in range(len(mean_r))]
        res = minimize(thisstd, x_init, method = 'SLSQP', 
                       constraints = constraint, bounds = bound)
        resweights = res.x
        resstd = res.fun
        resweightslis.append(list(resweights))
        resstdlis.append([resstd, r, list(resweights)])
    return {'resweightslis': resweightslis, 'resstdlis': resstdlis}