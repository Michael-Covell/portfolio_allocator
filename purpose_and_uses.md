# Purpose and Uses

portfolio_allocator is for anyone who has a target allocation for their portfolio and a lump sum of cash to invest.  But no matter who is using it and what the intended purposes, the consequences of its use may be significant.  portfolio_allocator optimizes the calculation of allotments of a lump sum to investments in a portfolio. 
 In practice, the "portfolio" may be limited to securities like stocks and bonds or include a variety of asset classes and purposes such real estate investments, fundraising goals, and recipients of funding such as nonprofit organizations and government sponsored programs.  In large portfolios, the way in which a lump sum is divided and allocated at a particular point in time may meaningfully impact the collective performance of these assests and/or funding recipients.  Thus, it is important to consider how different methods of calculating allotments affect the ultimate composition of a portfolio.

## Why should you use portfolio_allocator?

Usually, the target allocation of a portfolio is elusive because the values of investments change over time, or the needs of funding recipients and availability of funding emerge on different timelines.  As a result, there is measurable error in the current values relative to the target values of each investment; or, in the context of beneficiary funding, there is error in the cumulative sum of previous distributions to funding recipients relative to each recipients' target allocation.  To correct these errors, investors may hypothetically rebalance the portfolio such that they sell portions of investments that exceed target values and purchase more of investments that fall short of target values.

In many situations however, this is neither desirable nor possible.  Selling investments is often a taxable event that investors want to avoid.  Likewise, administrators of funding cannot move distributed funds from one recipient to another once they have been distributed.  As an alternative, investors may try to meet their target allocation incrementally through the investment of funds as they become available.  For a portfolio of stocks, this would mean purchasing more shares of investments that are below target values and not buying shares of investments that exceed target values.  portfolio_allocator optimizes this approach by calculating allotment amounts that will render a portfolio matching the target allocation as closely as possible.

## How does it work?

portfolio_allocator calculates the difference between target and current values of investments (i.e., deficits) and the difference between target and current proportions (i.e., allocation error).  These variables are then used to calculate allotment sets that will bring the ultimate composition of the portfolio closer to the target allocation specified by the user.  

Method 1 is the allocate_by_rank method.  This method allocates a lump sum to eliminate the deficits in rank order until the lump sum is gone.  For example, if the lump sum is $3 and the two top ranking deficits are each $2, this method will result in an allotment of $2 to the investment with the top ranking deficit and $1 to the investment with the second-ranking deficit.  In this example, the error for the first investment will be reduced to zero while the error for the remaining investments may still be significant.  This is considered a suboptimal allotment set because it biasly favors the invesments with the larger, higher-ranking deficits.  The optimal result would be a set of allotments that minimize allocation error across investments thereby bringing all investments as close as possible to the target allocation.

Method 2, the the allocate_for_minimal_errors method, is designed to achieve this.  Rather than reducing deficits, Method 2 first calculates the minimum possible error for all investments with a deficit greater than 0 and then calculates the allotments required to produce those errors. Sometimes however, this can result in negative allotment values when one or more investments have a relatively small error in the current portfolio. To prevent such impractical allotment values, Method 2 iteratively calculates allotments and constant errors for each investment.  If any allotment values are negative, the negative allotment term is dropped from the subsequent calculations and iteration continues. Iteration ends once the non-negative constraint for allotments is satisfied.


## How do I use portfolio_allocator?
portfolio_allocator is a function written in python.  It can be imported using the py file in this repository.  The function returns a pandas DataFrame containing the results of the two methods.  To do this, portolio_allocator takes three arguments:
* `cash` (integer, float) is the lump sum of money to be allocated to investments.
* `target_pcts` (iterable container of floats) are the set of target allocations specified as proportions that sum to 1.
* `current_values` (iterable container of integers or floats) are the current values of the investments in the portfolio (or cumulative sum of distributions to funding recipients).

These parameters are used to create a pandas DataFrame with five calculated columns:
* The 'current%' column contains the proportions of the current values of investments in the portfolio
* The 'target_value' column contains values determined by the target allocations AFTER `cash` has been distributed
* The 'deficit' column is the target value minus the current value
* The 'error' column is the difference between `target_pcts` and 'current%'
* The 'rank' column contains the rankings of deficits in decending order such that the largest deficit is assigned a rank of zero

### How to Interpret the Results
The final DataFrame returned by portfolio_allocator contains columns for `target_pcts`, `current_values` and each calculated column.  In addition, it contains columns for the allotment sets generated by Methods 1, 'allocate_by_rank', and 2, 'allocate_for_minimal_errors'.  Two columns contain allocation errors corresponding to the  hypothetical portfolio composition that would be achieved if the allotment sets generated by Methods 1 and 2 were implemented.  Column 'errors_m1' contains the allocation errors that corresponds to Method 1's allotment set.  Column 'errors_m2' contains the allocation errors that corresponds to Method 2's allotment set.

### Want more Details?

A detailed illustration of how each method works is provided in the supplementary ipynb notebook file included in this repository (see [A Guided Tour of portfolio_allocator](portfolio_allocator_tour.md)).  Note that while the portfolio size and allotment amounts are relatively small in this illustration, the difference between optimal and suboptimal allotment sets may have significant consequences for larger portfolios with larger allocation amounts.  
