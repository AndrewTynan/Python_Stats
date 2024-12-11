
# **Overview**
# * Using a simulation to compare Welch Two Sample t-test and the Two Proportions z-test 
# * Variables of interest: `baseline_rate`, `mde`, `population`, and `control_ratio` 
#   * The `baseline_rate` are:
#     * Long-term is 61.5%
#     * Short-term is 90% 
#     * **Note these data points are from September and we are working to get more recent data** 
#   * The `mde` (minimum detectable effect) is designed as: 
#     * Long-term uses 2%
#     * Short-term uses 0.2%
#   * The `population` is designed as: 
#     * Long-term is 200K new monthly subscribers 
#     * Short-term is 3M existing monthly subscribers 
#     * **Note these data points are from September and we are working to get more recent data** 
#   * The `control_ratio` means the imbalance between the *control* and *exposed* segments     
#     * For A/B tests are designed to use: 
#       * Long-term uses a 5% control which is a ratio of 19:1 between exposed to control
#       * Short-term uses a 2% control which is a ratio of 49:1 between exposed to control  

# **Test**
# * Using [pingouin](https://pingouin-stats.org/build/html/index.html) and it's [Welch's t-test](https://pingouin-stats.org/build/html/generated/pingouin.ttest.html) 
#   * At the bottom of the t-test link it mentions 'Independent two-sample T-test with unequal sample size. A Welch’s T-test is used.'
#     * This appears to be triggered automatically since there is not argument used in the example. 
#   * One limitation is the confidence interval is only to 2 decimal places
# * scipy.stats import ttest_ind does not appear to support Welch’s T-test 
# * However, statsmodels CompareMeans does does not appear to have Welch’s T-test
# * [Stackoverflow discussion](https://stackoverflow.com/questions/31768464/confidence-interval-for-t-test-difference-between-means-in-python) of the different options and also a 
# [stackexchange discussion](https://stats.stackexchange.com/questions/475289/confidence-interval-for-2-sample-t-test-with-scipy)  

# **Findings**
# * Welch Two Sample t-test and the Two Proportions z-test have the same t-statistic, p-value, and confidence intervals 
#   * Granted this is on a limited simulation
#   * Maybe they will vary across the range of varibles


from numpy.random import binomial
from numpy import log
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW  
from statsmodels.stats.proportion import test_proportions_2indep, confint_proportions_2indep 
from plotnine import *
from plotnine.data import mtcars
import matplotlib 
# from mizani.formatters import percent_format
import math 
import pandas as pd 


def extract_t_test(t_test_results, t_test_CIs): 

    # NOTE: a helper function to extract the values of interest from the t-test output
    # t_res is output from statsmodels CompareMeans
    # t_CIs is output from statsmodels CompareMeans
    t_test_output = pd.DataFrame({'t statistic': t_test_results[0],
                                  'pvalue':      t_test_results[1], 
                                  'low_CI':      t_test_CIs[0], 
                                  'high_CI':     t_test_CIs[1]}, index=[0])  

    return t_test_output

print(extract_t_test(tt, tt_CIs)) 


# DEFINE sim()
def sim(baseline_rate, mde, population, control_ratio, samples): 
    samples = samples + 1 
    params  = pd.DataFrame({'baseline_rate': baseline_rate, 
                            'mde':           mde, 
                            'population':    population,
                            'control_ratio': control_ratio}, index=[0]) 
    
    for i in range(1,samples): 

        control_n = math.ceil(population / control_ratio) 
        exposed_n = population - control_n 

        control_retention = math.ceil(control_n * (baseline_rate + mde))  
        exposed_retention = math.ceil(exposed_n * baseline_rate)

        control_sample = binomial(1, (baseline_rate + mde), size = control_n) 
        exposed_sample = binomial(1, baseline_rate,         size = exposed_n) 

        cm         = CompareMeans(DescrStatsW(control_sample), DescrStatsW(exposed_sample))
        t_test     = cm.ttest_ind(alternative     = 'larger', usevar = 'unequal') # NOTE: If unequal, then Welch ttest with Satterthwait degrees of freedom is used
        t_test_CIs = cm.tconfint_diff(alternative = 'larger', usevar = 'unequal')     

        t_test_output = extract_t_test(t_test, t_test_CIs)     
        t_test_output.insert(0, "test", ['t test'], True)
        t_test_output = pd.concat([t_test_output, params], axis=1) 

        control_sample_df = pd.DataFrame(control_sample)
        control_sample_df = control_sample_df.rename(columns={control_sample_df.columns[0]: 'values'}) 

        exposed_sample_df = pd.DataFrame(exposed_sample)
        exposed_sample_df = pd.DataFrame(exposed_sample).rename(columns={exposed_sample_df.columns[0]: 'values'}) 

        prop_test = test_proportions_2indep(count1      = int(control_sample_df.query('values == 1').groupby(['values']).size()), 
                                            nobs1       = int(len(control_sample_df)),
                                            count2      = int(exposed_sample_df.query('values == 1').groupby(['values']).size()),
                                            nobs2       = int(len(exposed_sample_df)),
                                            alternative = 'larger')

        prop_test_ci = confint_proportions_2indep(count1 = int(control_sample_df.query('values == 1').groupby(['values']).size()), 
                                                  nobs1  = int(len(control_sample_df)),
                                                  count2 = int(exposed_sample_df.query('values == 1').groupby(['values']).size()),
                                                  nobs2  = int(len(exposed_sample_df)))  

        prop_test_output = pd.DataFrame({'test':        ['prop test'],
                                         't statistic': [prop_test.statistic],
                                         'pvalue':      [prop_test.pvalue],
                                         'low_CI':      [prop_test_ci[0]],
                                         'high_CI':     float('inf')})   # [prop_test_ci[1]]
        prop_test_output = pd.concat([prop_test_output, params], axis=1)  

        if i == 1: 
            t_test_results    = t_test_output
            prop_test_results = prop_test_output
        else:
            t_test_output.reset_index(drop=True, inplace=True)
            t_test_results = pd.concat([t_test_results, t_test_output], ignore_index=True, axis=0)
            prop_test_results.reset_index(drop=True, inplace=True) 
            prop_test_results = pd.concat([prop_test_results, prop_test_output], ignore_index=True, axis=0)     

        output = pd.concat([t_test_results, prop_test_results], ignore_index=True, axis=0) 

    return output 


# CHECK sim() 
baseline_rate = 0.615
mde = 0.02
population = 200000
control_ratio = 19 

results = sim(baseline_rate = baseline_rate, 
              mde           = mde,
              population    = population, 
              control_ratio = control_ratio,
              samples       = 3)

results

# POC sim_runner() for long-term (e.g. new subscribers)

samples        = 50
baseline_rates = [0.55, 0.60, 0.65] 
mdes           = [0.02, 0.03, 0.04] 
populations    = [175000, 200000, 225000] 
control_ratios = [5.66, 9, 19] 

if 'sim_results' in locals():
    del(sim_results) 

for baseline_rate in baseline_rates: 
    for mde in mdes: 
        for population in populations: 
            for control_ratio in control_ratios: 

                sim_output = sim(baseline_rate = baseline_rate, 
                                 mde           = mde,
                                 population    = population, 
                                 control_ratio = control_ratio,
                                 samples       = samples) 

                if 'sim_results' not in locals(): 
                    sim_results = sim_output
                else: 
                    sim_results = pd.concat([sim_results, sim_output], ignore_index=True, axis=0) 

# sim_results.head(20)

# DEFINE sim_runner()
def sim_runner(baseline_rate, mde, population, control_ratio, samples): 

    for baseline_rate in baseline_rates: 
        for mde in mdes: 
            for population in populations: 
                for control_ratio in control_ratios: 

                    sim_output = sim(baseline_rate = baseline_rate, 
                                     mde           = mde,
                                     population    = population, 
                                     control_ratio = control_ratio,
                                     samples       = samples) 

                    if 'sim_results' not in locals(): 
                        sim_results = sim_output
                    else: 
                        sim_results = pd.concat([sim_results, sim_output], ignore_index=True, axis=0) 
    
    return sim_results

# RUN sim_runner() for long-term  (e.g. new subscribers)

sample        = 500
baseline_rate = [0.55, 0.60, 0.65] 
mde           = [0.02, 0.03, 0.04] 
population    = [175000, 200000, 225000] 
control_ratio = [5.66, 9, 19] 

new_subscribers_sim = sim_runner(baseline_rate, mde, population, control_ratio, sample)
new_subscribers_sim.shape


# CHECK
vars = ['test', 'baseline_rate', 'mde', 'population', 'control_ratio']
check_2 = pd.DataFrame((new_subscribers_sim
                        .groupby(vars)
                        .size()))
print(check_2.to_string())  


# CHECK
print("Unique values:") 
for var in vars: 
    u = new_subscribers_sim[var].unique()
    print("%s: %s" % (var, u))


# POC boxplot_jitter 
(pn.ggplot(new_subscribers_sim) + 
    pn.aes(x = 'test', y = 'low_CI', color = "factor(test)") + 
    # pn.facet_grid('test ~ baseline_rate', scales='free') + 
    pn.geom_boxplot(color = 'black') +
    pn.geom_jitter(alpha = 0.2) + 
    pn.scale_y_continuous(labels=percent_format()) +
    pn.guides(color = pn.guide_legend(title = "Test")) +    
    pn.labs(title = 'Confidence Intervals by Test Type',
            subtitle = 'Sim Confidence Intervals', 
            caption = 'For 10K Simualted')) 


# DEFINE boxplot_jitter()
def boxplot_jitter(df, x, y, color):

    plt = (pn.ggplot(df) + 
            pn.aes(x = x, y = y, color = color) + 
            pn.geom_boxplot(color = 'black') +
            pn.geom_jitter(alpha = 0.02) + 
            pn.scale_y_continuous(labels=percent_format()) +
            pn.guides(color = pn.guide_legend(title = "Test"))) 
    
    return plt 

# PLOT NOTE CI high level
test_low_CI_plt = boxplot_jitter(df   = new_subscribers_sim, 
                                 x    = 'test', 
                                 y    = 'low_CI', 
                                color = "factor(test)") 

(test_low_CI_plt + 
    pn.labs(title    = 'T-test vs Prop-Test Confidence Interval For 500 Simulations',
            subtitle = "Conditions: One-sided 'larger' and unequal variance", 
            caption  = '''Details: 
samples        = 500
baseline_rates = [0.55, 0.60, 0.65] 
mdes           = [0.02, 0.03, 0.04] 
populations    = [175000, 200000, 225000] 
control_ratios = [5.66, 9, 19]''') + 
    pn.theme(figure_size = (8, 4),
             legend_position='none'))


# PLOT NOTE many CI boxplots
(test_low_CI_plt + 
    pn.facet_grid('baseline_rate + mde ~ population + control_ratio', scales='free') +
    pn.labs(title    = "T-test vs Prop-Test Confidence Interval For 500 Simulations \n\n Conditions: One-sided 'larger' and unequal variance",
            subtitle = 'By baseline_rate + mde ~ population + control_ratio', 
            caption  = '''Details: 
samples        = 500
baseline_rates = [0.55, 0.60, 0.65] 
mdes           = [0.02, 0.03, 0.04] 
populations    = [175000, 200000, 225000] 
control_ratios = [5.66, 9, 19]''') + 
    pn.theme(figure_size = (16, 12),
             legend_position='none'))


# CHECK
# (new_subscribers_sim_results
#  .loc[:, ['test', 'baseline_rate', 'mde', 'population', 'control_ratio','low_CI']]
# #  .wide_to_long(df, stubnames='ht', i=['famid', 'birth'], j='age')
#  .head())


# DEFINE 
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
            # .iloc[:,[0,10,1,2,3,4,5,6,7,8,9]]
            ) 

    return df


vars = ['test', 'baseline_rate'] # 'mde', 'population', 'control_ratio'
new_subs_sim_test_basel_five_num_sum = five_num_sum_by_group(new_subscribers_sim, vars, 'low_CI') 
new_subs_sim_test_basel_five_num_sum = new_subs_sim_test_basel_five_num_sum.iloc[:,[0,1,10,2,3,4,5,6,7,8,9]] 

print('Only sharing high level summary stats to limit the rows')
new_subs_sim_test_basel_five_num_sum

# PLOT NOTE p-value high level 
new_subscribers_sim["pvalue_log"] = log(new_subscribers_sim["pvalue"]) 

test_pvalue_plt = boxplot_jitter(df   = new_subscribers_sim, 
                                 x    = 'test', 
                                 y    = 'pvalue_log', 
                                color = "factor(test)") 

(test_pvalue_plt + 
    pn.labs(title    = "T-test vs Prop-Test P-value For 500 Simulations \n\n Conditions: One-sided 'larger' and unequal variance", 
            subtitle = 'Using log transformation to improve the visualzation due to the highly non-normal / exponential distribution', 
            caption  = '''Details: 
samples        = 500
baseline_rates = [0.55, 0.60, 0.65] 
mdes           = [0.02, 0.03, 0.04] 
populations    = [175000, 200000, 225000] 
control_ratios = [5.66, 9, 19]''') +    
    pn.theme(figure_size =(12, 5))) 


# PLOT NOTE many CI boxplots
(test_pvalue_plt + 
    pn.facet_grid('baseline_rate + mde ~ population + control_ratio', scales='free') +
    pn.labs(title    = "T-test vs Prop-Test P-value For 500 Simulations \n\n Conditions: One-sided 'larger' amd unequal variance", 
            subtitle = 'Using log transformation to improve the visualzation due to the highly non-normal / exponential distribution', 
            caption  = '''Details: 
samples        = 500
baseline_rates = [0.55, 0.60, 0.65] 
mdes           = [0.02, 0.03, 0.04] 
populations    = [175000, 200000, 225000] 
control_ratios = [5.66, 9, 19]''') + 
    pn.theme(figure_size = (16, 12))) 


vars = ['test', 'baseline_rate'] # 'mde', 'population', 'control_ratio'
new_subs_sim_test_basel_five_num_sum = five_num_sum_by_group(new_subscribers_sim, vars, 'pvalue') 
new_subs_sim_test_basel_five_num_sum = new_subs_sim_test_basel_five_num_sum.iloc[:,[0,1,10,2,3,4,5,6,7,8,9]] 

print('Note: the p-values skew extremely small') 
print('Only sharing high level summary stats to limit the rows')
new_subs_sim_test_basel_five_num_sum


# RUN sim_runner() for short-term  (e.g. existing subs)

samples        = 500
baseline_rates = [0.85, 0.90, 0.95] 
mdes           = [0.01, 0.02, 0.03] 
populations    = [2750000, 3000000, 3250000] 
control_ratios = [19, 32.33, 49] 

existing_subscribers_sim = sim_runner(baseline_rate, mde, population, control_ratio, samples)
existing_subscribers_sim.shape


# PLOT NOTE CI high level
existing_CI_plt = boxplot_jitter(df    = existing_subscribers_sim, 
                                 x     = 'test', 
                                 y     = 'low_CI', 
                                 color = "factor(test)") 

(existing_CI_plt + 
    pn.labs(title    = 'Existing Subscribers T-test vs Prop-Test Confidence Interval For 500 Simulations',
            subtitle = "Conditions: One-sided 'larger' and unequal variance", 
            caption  = '''Details: 
samples        = 500
baseline_rates = [0.85, 0.90, 0.95] 
mdes           = [0.01, 0.02, 0.03] 
populations    = [2750000, 3000000, 3250000] 
control_ratios = [19, 32.33, 49]''') + 
    pn.theme(figure_size = (8, 4),
             legend_position='none'))






