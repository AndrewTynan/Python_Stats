
t_test_results, t_test_agg_results = test_runner(new_subs_user_level,              # new_subs_user_level, df_2023_06
                                                 test   = 't-test',       
                                                 metric = 'is_retained', 
                                                 period = 'cumulative',   
                                                 groups = ['is_longterm']) 

pd.options.display.float_format = '{:.2f}'.format 
pd.set_option('display.max_rows', None) 
t_test_results 



pd.options.display.float_format = '{:.2f}'.format 
t_test_agg_results.sort_values(by =  ['lifetime_month', 'is_group_member'], ascending = True) 


(col_plot(t_test_agg_results, 'factor(lifetime_month)', 'retention_rate', 'is_group_member', 
          text = 'retention_rate', 
          percent = 'retention_rate',   
          position = 'dodge',
          percent_deciamls = 1) + 
theme(figure_size = (16, 4),
      legend_position='bottom') + 
labs(title="Cumulative Retention by Long Term  Status Lifetime Month",
     x = 'Lifetime Month')) 



t_test_results, t_test_agg_results = test_runner(new_subs_user_level,              # new_subs_user_level, df_2023_06 
                                                 test   = 't-test',      
                                                 metric = 'is_retained', 
                                                 period = 'prior',  
                                                 groups = ['is_group_member']) 
t_test_results 


pd.options.display.float_format = '{:.2f}'.format 
t_test_agg_results.sort_values(by = ['lifetime_month', 'is_group_member'], ascending = True) 


(col_plot(t_test_agg_results, 'factor(lifetime_month)', 'retention_rate', 'is_group_member', 
          text = 'retention_rate', 
          percent = 'retention_rate', 
          position = 'dodge',
          percent_deciamls = 1) + 
theme(figure_size = (16, 4),
      legend_position='bottom') + 
labs(title="Prior Month Retention by Long Term  Status Lifetime Month",
     subtitle='Note: the large drop in month 4 is due to the large November cohort',
     x = 'Lifetime Month')) 


anova_tier_type_test_results, anova_tier_type_df_agg_results = test_runner(new_subs_user_level, 
                                                                            test   = 'anova',        # 't-test', 
                                                                            metric = 'is_retained', 
                                                                            period = 'cumulative',   # 'prior'
                                                                            groups = ['is_group_member', 'tier_type']) # payment_provider
pd.options.display.float_format = '{:.2f}'.format 
pd.set_option('display.max_rows', None)
anova_tier_type_test_results 


(col_plot(anova_tier_type_df_agg_results, 'factor(lifetime_month)', 'retention_rate', 'is_group_member', 
          text = 'retention_rate', 
          percent = 'retention_rate', 
          position = 'dodge', 
          percent_deciamls = 0,
          facet = 'tier_type',
          nrow = 3) + 
theme(figure_size = (16, 10),
      legend_position='bottom') + 
labs(title="Cumulative Retention by Long Term  Status Lifetime Month",
     subtitle='By Tier Type',
     x = 'Lifetime Month')) 


anova_provider_test_results, anova_provider_df_agg_results = test_runner(new_subs_user_level, 
                                                                         test   = 'anova',       
                                                                         metric = 'is_retained', 
                                                                         period = 'cumulative',  
                                                                         groups = ['is_group_member', 'payment_provider']) 

pd.options.display.float_format = '{:.2f}'.format 
pd.set_option('display.max_rows', None)
anova_provider_test_results 


(col_plot(anova_provider_df_agg_results, 'factor(lifetime_month)', 'retention_rate', 'is_group_member', 
          text = 'retention_rate', 
          percent = 'retention_rate', 
          position = 'dodge', 
          percent_deciamls = 0,
          facet = 'payment_provider',
          nrow = 7) + 
theme(figure_size = (16, 10),
      legend_position='bottom') + 
labs(title="Cumulative Retention by Long Term  Status Lifetime Month",
     subtitle='By Tier Type',
     x = 'Lifetime Month')) 

