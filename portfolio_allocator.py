# The code herein is presented to illustrate two portfolio allocation methods (described below).  Following the imports of relevant libraries, 4 basic inputs are defined:
# - `cash` is the money to be allocated to investments
# - `target_pcts` are the set of target allocations specified as proportions that sum to 1 (minus rounding error)
# - `current_values` are the current values of the investments in the portfolio
# 
# The utility of the portfolio allocation methods will vary depending on the inputs.  
# Sometimes, portfolio allocation is so straightforward, it requires little-to-no math.  
# Other times, portfolio allocation can require advanced methods.  
# The methods presented here are most useful when there are significant discrepancies between current and target values across many but not all investments, and there is a large amount of `cash` to allocate but not enough meet all target values.

import pandas as pd
import numpy as np

def portfolio_allocator(cash,current_values,target_pcts):
    # Data Preparation
    # the sum of target_pcts should equal 1
    assert round(sum(target_pcts)) == 1, 'sum of target % allocations do not equal zero'

    # Create DataFrame
    df = pd.DataFrame({'target%':target_pcts,'current_value':current_values})

    # Create calculated columns which will be used by the allocation methods below.
        # note that target values reflect cash as shown in calculation
    df['current%'] = df['current_value'] / df['current_value'].sum()
    df['target_value'] = df['target%'] * (df['current_value'].sum()+cash)
    df['deficit'] = df['target_value'] - df['current_value']
    df['error'] = (df['current_value'] / df['current_value'].sum()) - df['target%']

    # create 'rank column' to reflect rankings of deficits (i.e., discrepancies between the target and current values)
        # rankings are made in descending order such that the largest deficit gets a rank of 0
    df['rank'] = df['deficit'].rank(method='first',ascending=False).astype(int)-1

    # having the dataframe sorted by rank makes calculations subsequent easier to interpret
    df.sort_values(by='rank',inplace=True)


    # Method 1: allocate-by-rank
    # This method allocates cash to completely eliminate the deficits in rank order untill the cash is gone.  For example, if the cash is \\$3 and the two top ranking deficits are each \\$2, 
    # this method will result in an allocation of \\$2 to the top ranking deficit and \\$1 to the subsequent deficit.

    #define function to determine allocation based on the index of the DataFrame 
    #and the amount allocated so far
        #The function allocates an amount equal to the deficit or whatever dollars remain 
        #after accounting for previous allocations
        
    def determine_amount(i,allocated_so_far):
        if (df.loc[i,'deficit'] <= cash - allocated_so_far) & (df.loc[i,'deficit']>=0): 
            return df.loc[i,'deficit']
        elif (df.loc[i,'deficit'] >= cash - allocated_so_far) & (df.loc[i,'deficit']>=0): 
             return cash - allocated_so_far
        elif df.loc[i,'deficit'] < 0:
            return 0

    #find the allocation to each investment
    total_allocation = 0
    money = cash
    allocated_cumsum = 0
    for rank in df['rank']:
        b = df['rank']==rank
        index = df.loc[b].index[0]
        allocation = determine_amount(index,allocated_cumsum)
        df.loc[b,'allocate_by_rank'] = allocation
        allocated_cumsum += allocation
        money = cash - allocated_cumsum

    #calculate the error of the new values
    df['error2'] = ((df['current_value'] + df['allocate_by_rank']) / (df['current_value'].sum()+cash)) - df['target%']

    #make sure the sum of the allocations equals the cash
    assert round(df['allocate_by_rank'].sum()) == cash, "sum of Method 1 allocations does not equal cash"

    # # Method 2: allocate-for-equal-errors
    # Method 1 can lead to suboptimal results.  When allocating cash to elminate deficits, 
    # errors are reduced to zero for investments with the top ranking deficits, 
    # but may remain large for investments with lower ranking deficits.  The optimal result would be a set of allocations that minimizes all errors as much as possible.  
    # 
    # Method 2 achieves this by calculating the minimum possible error for all investments with a deficit greater than 0,
    # and then calculating the allocations required to produce those errors.

    # However, Method 2 can return impractical allocations when not needed. 
    # That is, when all error values for investments with deficits greater than zero 
    # are minimized by Method 1, Method 2 may return a set of allocations that includes negative numbers. 
    # Therefore, is it important to examine the error values produced by Method 1 
    # before proceeding to Method 2.

    #check to see if method 2 will be useful or not
    b1 = df['deficit'] >= 0
    b2 = df['allocate_by_rank'] > 0
    if df.loc[b1&b2,'error2'].abs().min() < df.loc[b1&~b2,'error2'].abs().max():
        print('Method 1 is suboptimal.')
        use_method2 = True
    else:
        print("Method 2 is unnecessary and may return an allocation set that includes negative numbers.")
        use_method2 = False

    if use_method2:
        #Calculate equal errors
        #The equation for e is derived from the system of equations presented above
        cv = df['current_value'].to_list()
        t_pct = df['target%'].to_list()
        deficit = df['deficit'].to_list()
        select_ranks = [i for i in range(len(df)) if deficit[i]>0]
        select_cv = sum([cv[i] for i in select_ranks])
        select_t_pct = sum([t_pct[i] for i in select_ranks])
        select_ranks_cnt = len(select_ranks)
        e = 1/select_ranks_cnt * ((select_cv + cash)/(sum(cv) + cash) - select_t_pct)

        #calculate cash allocations in a dictionary where keys are ranks and values are allocations
        #the equation for each allocation is derived from the system of equations presented above
        allocations = {i:((e + t_pct[i])*(sum(cv)+cash)) - cv[i] if i in select_ranks else 0 for i in range(len(df))}

        #create column containing allocations calculated via Method 2
        df['allocate_for_minimal_errors'] = df.apply(lambda r: allocations[r['rank']],axis=1)

        #Calculate errors based on Method 2 allocations
        df['error3'] = ((df['current_value'] + df['allocate_for_minimal_errors']) / (df['current_value'].sum()+cash)) - df['target%']

    return df

    # When the portfolio size and allocation amounts are small, 
    # the difference between optimal and suboptimal allocations may be negligible.  
    # However, when large, the difference may have significant consequences for 
    # larger portfolios with larger allocation amounts.  
    # In high stakes situations such as hedge funds, company-owned assests, 
    # or government budget distributions, or philanthropic initiatives, 
    # allocation methods could impact overall portfolio or program performance 
    # and the recipients of the funding determined by the allocation method.
