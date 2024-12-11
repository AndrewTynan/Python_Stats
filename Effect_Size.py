# Databricks notebook source
import statsmodels.stats.power as smp
import statsmodels.api as sm
import math

# COMMAND ----------

baseline_retention_rate = 0.615
mde_retention_rate = 0.635

alpha = 0.05 
power = 0.80 
N = 237600

effect_size = sm.stats.proportion_effectsize(baseline_retention_rate, mde_retention_rate)
effect_size = abs(effect_size)
print(effect_size)

sample_size = smp.NormalIndPower().solve_power(effect_size=effect_size, 
                                            #    nobs1=200000,
                                               alpha=alpha,
                                               power=power,
                                               ratio=19,
                                               alternative='larger')

math.ceil(sample_size)

# COMMAND ----------

# estimate sample size via power analysis
from statsmodels.stats.power import TTestIndPower

# parameters 
effect = 0.5
alpha = 0.05
power = 0.8

# perform power analysis
analysis = TTestIndPower()
# result = analysis.solve_power(effect, 
#                               power=power, 
#                               nobs1=None, 
#                               ratio=1.0, 
#                               alpha=alpha)

analysis.power(nobs1=22.959830247088764, effect_size=0.978343, alpha=0.05)                              

# print('Sample Size: %.3f' % result)
# result

# COMMAND ----------

# Import library 
import scipy.stats as stats 
import numpy as np 
  
# Creating data groups 
data_group1 = np.array([14, 15, 15, 16, 13, 8, 14, 
                        17, 16, 14, 19, 20, 21, 15, 
                        15]) 
data_group2 = np.array([36, 37, 44, 27, 24, 28, 27, 
                        39, 29, 24, 37, 32, 24, 26, 
                        33]) 
  
# Conduct Welch's t-Test and print the result 
print(stats.ttest_ind(data_group1, data_group2, equal_var = False)) 

# COMMAND ----------

import pandas as pd 

#create another example df 
points_df = pd.DataFrame({'team': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
                         'points': [18, 22, 19, 14, 14, 11, 20, 28],
                         'assists': [5, 7, 7, 9, 12, 9, 9, 4],
                         'rebounds': [11, 8, 10, 6, 6, 5, 9, 12],
                         'fouls': [11, 80, 10, 60, 6, 50, 9, 12]}) 

# add some cols to group by 
points_df['league'] = np.where(points_df['team'].isin(['A', 'B', 'C', 'D']), 'Major', 'Minor')
points_df['points_bucket'] = np.where(points_df['points'] >= 19, 'Upper', 'Lower')

points_df.head(2)

# COMMAND ----------

def five_num_sum_by_group(df, by, metric):

    def q1(x):
        return x.quantile(0.25)

    def q3(x):
        return x.quantile(0.75)

    df = (df
            .groupby(by)
            .agg(count  = (metric, 'count'),
                mean    = (metric, 'mean'),
                std     = (metric, 'std'),
                min     = (metric, 'min'),
                q1      = (metric, q1),
                median  = (metric, 'median'),
                q3      = (metric, q3),
                max     = (metric, 'max'),
            ).reset_index() 
            .assign(metric = metric)
            .iloc[:,[0,10,1,2,3,4,5,6,7,8,9]] 
        ) 

    return df

test = five_num_sum_by_group(points_df, ['team', 'league','points_bucket'], 'points') 
test

# COMMAND ----------

def q1(x):
    return x.quantile(0.25)

def q3(x):
    return x.quantile(0.75)

(points_df
    .groupby(['league','points_bucket'])
    .agg(count  = ('points', 'count'),
        mean    = ('points', 'mean'),
        std     = ('points', 'std'),
        min     = ('points', 'min'),
        q1      = ('points', q1),
        median  = ('points', 'median'),
        q3      = ('points', q3),
        max     = ('points', 'max'),
    ).reset_index() 
    .assign(metric = 'points') 
    .iloc[:,[0,1,10,2,3,4,5,6,7,8,9]] 
) 

# COMMAND ----------

# MAGIC %sql
# MAGIC

# COMMAND ----------


