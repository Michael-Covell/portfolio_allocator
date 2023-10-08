import pandas as pd
import numpy as np

def portfolio_allocator(cash,current_values,target_pcts):
    """
    Allocate a given amount of cash to a portfolio based on target percentages.
    
    Parameters:
        - cash (int): The amount of cash available for allocation.
        - current_values (list or array-like): Current values of each investment in the portfolio.
        - target_pcts (list or array-like): Target percentages for each investment in the portfolio. 
          The sum of target percentages should equal 1.
    
    Returns:
        pandas.DataFrame: A DataFrame containing allocation details, including target percentages, current percentages,
        target values, current values, ranks, deficits, errors, and allotments from two allocation methods.
    
        Columns in the Returned DataFrame:
        - 'target%' (float): Target percentage allocation for each investment.
        - 'current%' (float): Current percentage allocation for each investment.
        - 'target_value' (float): Target value for each investment based on target percentages.
        - 'current_value' (float): Current value of each investment.
        - 'rank' (int): Rank of deficits in descending order.
        - 'deficit' (float): Difference between target value and current value.
        - 'error' (float): Difference between target percentage and current percentage, i.e., allocation error.
        - 'allocate_by_rank' (float): Allotment amount for each investment using the allocate-by-rank method.
        - 'error_m1' (float): Allocation error of new percentages if allocate-by-rank (i.e., Method 1) allotments were made.
        - 'allocate_for_minimal_errors' (float): Allotment amount for each investment using the allocate-for-minimal-errors method.
        - 'error_m2' (float): Allocation error of new percentages if allocate-for-minimal-errors (i.e., Method 2) allotments were made.
    
    Allotment Calculation Methods:
        1. Allocate-by-Rank: Cash is allocated to eliminate deficits in descending order of their ranks.
        2. Allocate-for-Minimal-Errors: Cash is allocated to minimize allocatoin error in the portfolio.
    
    
    Example:
     cash = 1000
     current_values = [500, 300, 200]
     target_pcts = [0.4, 0.4, 0.2]
     result_df = portfolio_allocator(cash, current_values, target_pcts)
    """
    
    
    # Data Preparation

    # Round down to elminate rounding error in subsequent calculations which may trigger unwanted assertion errors
    cash = int(cash)
    # The sum of target_pcts should equal 1
    assert round(sum(target_pcts)) == 1, 'sum of target % allocations do not equal zero'

    # Create DataFrame
    df = pd.DataFrame({'target%':target_pcts,'current_value':current_values})

    # Create calculated columns which will be used by the allocation methods below.
        # Note that target values reflect cash as shown in calculation
    df['current%'] = df['current_value'] / df['current_value'].sum()
    df['target_value'] = df['target%'] * (df['current_value'].sum()+cash)
    df['deficit'] = df['target_value'] - df['current_value']
    df['error'] = (df['current_value'] / df['current_value'].sum()) - df['target%']

    # Create 'rank column' to reflect rankings of deficits (i.e., discrepancies between the target and current values)
        # Rankings are made in descending order such that the largest deficit gets a rank of 0
    df['rank'] = df['deficit'].rank(method='first',ascending=False).astype(int)-1

    # Having the dataframe sorted by rank makes calculations subsequent easier to interpret
    df.sort_values(by='rank',inplace=True)

    # Reorder columns
    for col in reversed(('target%','current%','target_value','current_value','rank','deficit','error')):
            extracted_col = df.pop(col)
            df.insert(0, col, extracted_col)


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
    df['error_m1'] = ((df['current_value'] + df['allocate_by_rank']) / (df['current_value'].sum()+cash)) - df['target%']

    #make sure the sum of the allocations equals the cash
    assert round(df['allocate_by_rank'].sum()) == cash, "sum of Method 1 allocations does not equal cash"

    # Method 2: allocate-for-equal-errors
    
    # Method 1 can lead to suboptimal results.  When allocating cash to elminate deficits, 
    # errors are reduced to zero for investments with the top ranking deficits, 
    # but may remain large for investments with lower ranking deficits.  The optimal result would be a set of allocations that minimizes all errors as much as possible.  
    # 
    # Method 2 achieves this by calculating the minimum possible error 
    # for all investments with a deficit greater than 0,
    # and then calculating the allotments required to produce those errors.  
    # Sometimes, this results in negative allotment values when 1 or more 
    # investments have a relatively small error in the current portfolio.
    # To prevent negative values which are impractical allotment values, 
    # Method 2 iteratively calculates allotments and constant errors for each investment
    # If any allotment values are negative, the negative allotment term is dropped
    # from the subsequent calculations and iteration continues.
    # Iteration ends once the non-negative constraint for allotments is satisfied.
    
    cv = df['current_value'].to_list()
    t_pct = df['target%'].to_list()
    deficit = df['deficit'].to_list()
    ranks_select = [i for i in range(len(df)) if deficit[i]>0]
    success = False
    
    while not success:
        #Calculate equal errors
        cv_select = sum([cv[i] for i in ranks_select])
        t_pct_select = sum([t_pct[i] for i in ranks_select])
        cnt = len(ranks_select)
        e = 1/cnt * ((cv_select + cash)/(sum(cv) + cash) - t_pct_select)
    
        # Calculate cash allocations in a dictionary where keys are ranks and values are allotments
        # The equation for each allotment is derived from the system of equations presented above
        allotments = {i:((e + t_pct[i])*(sum(cv)+cash)) - cv[i] if i in ranks_select else 0 for i in range(len(df))}
    
        # Check if the non-negative constraint is satisfied
        if all(val >= 0 for val in allotments.values()):
            success = True
        else:
            ranks_select = [rank for rank,allotment in allotments.items() if allotment > 0]
    
    # Create column containing allotments calculated via Method 2
    df['allocate_for_minimal_errors'] = df.apply(lambda r: allotments[r['rank']],axis=1)
    
    # Calculate errors based on Method 2 allotments
    df['error_m2'] = ((df['current_value'] + df['allocate_for_minimal_errors']) / (df['current_value'].sum()+cash)) - df['target%']
  
    return df


