
from statsmodels.stats.proportion import test_proportions_2indep, confint_proportions_2indep 


def prop_test(df, month, group_var): 
    # NOTE month is just for adding a data labels in params   

    # group_var conditon needs to be adjusted 

    retained = int(df.query("group_var == 'Yes'").loc[:,['retained_count_total']].values[0])
    total    = int(df.query("group_var == 'Yes'").loc[:,['cohort_count_total']].values[0])

    non_retained = int(df.query("group_var == 'No'").loc[:,['retained_count_total']].values[0])
    non_total    = int(df.query("group_var == 'No'").loc[:,['cohort_count_total']].values[0])    

    prop_test = test_proportions_2indep(count1      = non_retained, 
                                        nobs1       = non_total,
                                        count2      = retained,
                                        nobs2       = total) # alternative = 'larger') 

    prop_test_ci = confint_proportions_2indep(count1 = non_retained,
                                              nobs1  = non_total,
                                              count2 = retained,
                                              nobs2  = total) 

    prop_test_output = pd.DataFrame({'test':      ['prop test'],
                                     'statistic': [prop_test.statistic],
                                     'pvalue':    [prop_test.pvalue],
                                     'CI Lower':  [prop_test_ci[0]],
                                     'CI Upper':  [prop_test_ci[1]]}) 

    params           = pd.DataFrame({'month': month}, index=[0]) 
    prop_test_output = pd.concat([params, prop_test_output], axis=1)  

    return prop_test_output 
    

def prop_test_runner(df, group_var): 

    # group_var conditon needs to be adjusted 

    lifetime_months = df.loc[:, 'lifetime_month'].unique()

    for month in lifetime_months: 
        
        lifetime_months_var = f"lifetime_month == {month}" 

        df_agg = (df
                    .query(lifetime_months_var) 
                    .loc[:, ['lifetime_month', 'group_var', 'cohort_count', 'retained_count']]
                    .groupby(['lifetime_month', 'group_var'])
                    .agg(cohort_count_total  = ('cohort_count', 'sum'),
                        retained_count_total = ('retained_count', 'sum'))
                    .reset_index())  

        prop_test_output             = prop_test(df_agg, month)
        prop_test_output['stat_sig'] = prop_test_output['pvalue'].apply(lambda x: 'Yes' if x <= 0.05 else 'No') 

        df_agg = (df_agg
                  .assign(retained_percent = lambda x: ((x['retained_count_total'] / x['cohort_count_total']) * 100).round(2)))  

        if 'prop_test_results' not in locals(): 
            prop_test_results = prop_test_output 
            df_agg_results    = df_agg

        else: 
            prop_test_results = pd.concat([prop_test_results, prop_test_output], ignore_index=True, axis=0) 
            df_agg_results    = pd.concat([df_agg_results, df_agg], ignore_index=True, axis=0) 

    return prop_test_results, df_agg_results 
