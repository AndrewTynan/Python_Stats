
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW  


def extract_t_test(t_test_results, t_test_CIs): 

    # NOTE: a helper function to extract the values of interest from the t-test output
    t_test_output = pd.DataFrame({'t statistic': t_test_results[0],
                                  'pvalue':      t_test_results[1], 
                                  'CI Lower':    t_test_CIs[0],
                                  'CI Upper':    t_test_CIs[1]}, index=[0])  

    return t_test_output


def t_test(df, month, metric): 
    # NOTE month is just for adding a data labels 

    control = (df
                .query("group_var == 'Yes'")
                .loc[:, metric] 
                .to_list()) 
    exposed = (df
                .query("group_var == 'No'")
                .loc[:, metric] 
                .to_list()) 

    cm         = CompareMeans(DescrStatsW(exposed), DescrStatsW(control))
    t_test     = cm.ttest_ind(usevar = 'unequal')     # NOTE: If unequal, then Welch ttest is used.   alternative = 'larger',
    t_test_CIs = cm.tconfint_diff(usevar = 'unequal') # alternative = 'larger', 

    t_test_output = extract_t_test(t_test, t_test_CIs) 
    t_test_output.insert(0, "test", ['t test'], True) 

    params        = pd.DataFrame({'month': month}, index=[0]) 
    t_test_output = pd.concat([params, t_test_output], axis=1)  

    return t_test_output


def report_metric(df, stat, groups): 

    if stat == "retention_rate": 

        groupby = ['lifetime_month_ref'] + groups     # lifetime_month_ref
        
        df_base = (df
                    .groupby(groupby)
                    .agg(total_count = ('user_id', 'count'))  
                    .reset_index()) 

        df_retained = (df
                        .query('is_retained == 1') 
                        .groupby(groupby)
                        .agg(churned_count = ('user_id', 'count')))  

        df_agg_output = (pd.merge(df_base,
                                  df_retained, 
                                  on = groupby)
                            .assign(retention_rate = lambda x: ((x['churned_count'] / x['total_count']) * 100).round(3)))    
    
    # elif stat IN ('list of engagement metrics'):  
    #     df_base = (df
    #                 .query("is_base_population == 'Yes'") 
    #                 .groupby(['lifetime_month_ref', 'group_var'])
    #                 .agg(total_user_id_count  = ('user_id', 'count'), 
    #                      mean                 = (metric, 'mean'),
    #                      std                  = (metric, 'std'))
    #                 .reset_index())  

    #     df_base
    #     df_agg_output 
        
    return df_agg_output


# DEFINE test_runner() 

def test_runner(df_n, test, metric, period, groups): 
    # test:   't-test', 'anova' 
    # metric: 'is_retained'           # NOTE can update to engagement metrics 
    # period: 'prior', 'cumulative'     
    # groups: a list with any single value or combination of values: 'group_var', tier_type' & 'payment_provider' 

    lifetime_months = df_n.loc[:, 'lifetime_month'].unique().tolist()
    lifetime_months.sort() 

    if period == 'prior': 
        lifetime_months = lifetime_months[:-1] 
    elif period == 'cumulative': 
        lifetime_months.pop(0) 
        lifetime_months = lifetime_months[:-1] 

    for lifetime_month in lifetime_months: 
        df = df_n
        df['lifetime_month_ref'] = lifetime_month
        df['is_retained']        = df['lifetime_month'].apply(lambda x: 1 if x > lifetime_month else 0) 

        if period == 'prior':
            df['is_eligible_population'] = np.where((df['lifetime_month'] >= (lifetime_month - 1))  
                                                    & (df['potential_lifetime_month'] >= lifetime_month), 'Yes','No') 

        elif period == 'cumulative':
            df['is_eligible_population'] = df['potential_lifetime_month'].apply(lambda x: 'Yes' if x >= lifetime_month else 'No') 

        df = df.query("is_eligible_population == 'Yes'") 

        if test == 't-test': 
            test_output             = t_test(df, lifetime_month, metric) 
            test_output['stat_sig'] = test_output['pvalue'].apply(lambda x: 'Yes' if x <= 0.05 else 'No') 

        elif test == 'anova': 
            test_output = df.anova(dv      = 'is_retained', 
                                   between = groups).round(2)   
            params      = pd.DataFrame({'month': lifetime_month}, index=[0]) 
            test_output = pd.concat([params, test_output], axis=1)  
            test_output['month'] = lifetime_month # corrects nulls in month caused by concat-ing a scale params df to test_output

        df_agg = report_metric(df, 'retention_rate', groups) 

        df = df.drop(['is_retained', 'lifetime_month_ref', 'is_eligible_population'],  axis=1) # not sure this is needed..? 

        if 'test_results' not in locals(): 
            test_results = test_output 
            df_agg_results = df_agg 
        else: 
            test_results   = pd.concat([test_results, test_output], ignore_index=True, axis=0) 
            df_agg_results = pd.concat([df_agg_results, df_agg],    ignore_index=True, axis=0) 

    if period == 'prior': 
        test_results   =  test_results.query("month > 0")
        df_agg_results =  df_agg_results.query("lifetime_month_ref > 0")    

    df_agg_results = df_agg_results.rename(columns = {'lifetime_month_ref': 'lifetime_month'})

    return test_results, df_agg_results 

