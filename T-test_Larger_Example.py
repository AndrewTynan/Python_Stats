# Databricks notebook source
# MAGIC %md
# MAGIC ### Overview of Comparing Means Directionally
# MAGIC
# MAGIC * A two-sided two sample mean comparison just requires including each sample in the test  
# MAGIC   
# MAGIC * A one-sided two sample mean comparison requires specifying a 'base' and the other is either the 'larger' or 'smaller' comparison 

# COMMAND ----------

import pandas as pd 
import numpy as np
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW  
from statsmodels.stats.proportion import test_proportions_2indep, confint_proportions_2indep 

# COMMAND ----------

# MAGIC %md
# MAGIC ###t-test

# COMMAND ----------

df = pd.DataFrame({'sample_1': np.random.normal(loc=80, scale=2, size=100),
                   'sample_2': np.random.normal(loc=84.6, scale=2, size=100)}) 
df.head(2) 

# COMMAND ----------

(df
 .agg(sample_1_mean = ('sample_1', 'mean'),
      sample_1_std  = ('sample_1', 'std'),
      sample_2_mean = ('sample_2', 'mean'),
      sample_2_std  = ('sample_2', 'std')))

# COMMAND ----------

# cm           = CompareMeans(d1=DescrStatsW(data=df['sample_1']), d2=DescrStatsW(data=df['sample_2']))

cm           = CompareMeans(d1=DescrStatsW(data=df['sample_2']), d2=DescrStatsW(data=df['sample_1']))
t_test       = cm.ttest_ind(alternative = 'larger', usevar = 'unequal') # NOTE: If unequal, then Welch ttest with Satterthwait degrees of freedom is used
t_test_CIs   = cm.tconfint_diff(alpha=0.05, alternative = 'larger', usevar = 'unequal') 
lower, upper = cm.tconfint_diff(alpha=0.05, alternative='two-sided', usevar='unequal')

print(t_test) 
print(t_test_CIs) 
print(lower, upper) 

# COMMAND ----------



# COMMAND ----------

summary = cm.summary(use_t=True, alpha=0.05, usevar='pooled', value=0)
print(summary) 

# COMMAND ----------

# MAGIC %md
# MAGIC ###Prop-Test

# COMMAND ----------

#  prop_test = 
test_proportions_2indep(count1      = 1891185, 
                        nobs1       = 2363414,
                        count2      = 207376,
                        nobs2       = 245151,
                        alternative = 'larger') 

# COMMAND ----------

print(1891185. / 2363414)
207376. / 245151

# COMMAND ----------

# prop_test_ci = 
confint_proportions_2indep(count1 = 1891185,
                           nobs1  = 2363414,
                           count2 = 207376,
                           nobs2  = 245151) 

# COMMAND ----------


