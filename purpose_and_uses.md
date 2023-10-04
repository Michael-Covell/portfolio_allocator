# Purpose and Uses

portfolio_allocator is for anyone who has a target allocation for their portfolio and a lump sum of cash to invest.  In practice, the "portfolio" may be limited to securities like stocks and bonds or include a variety of assest classes, like real estate and venture capital.  Portfolios may also include fundraising goals, nonprofit organizations, or public sector programs.  Portfolio holders may be individuals or organizations.  In large portfolios different allotment sets may meaningfully impact the collective performance of the portfolio or funding recipients.  Thus, it is important to consider how different methods of calculating allotments affect the ultimate composition of a portfolio.  

## Why should you use portfolio_allocator?

Usually, the target allocation of a portfolio is elusive because the values of investments change over time, or the needs of funding recipients and availability of funding emerge on different timelines.  As a result, there is measurable error in the current values relative to the target values of each investment; or, in the context of budgetary funding, there is error in the cumulative sum of previous distributions to funding recipients relative to each recipients' approved budget.  To correct these errors, investors may hypothetically rebalance the portfolio such that they sell portions of investments that exceed target values and purchase more of investments that fall short of target values.

In many situations however, this is neither desirable nor possible.  Selling investments is often a taxable event that investors want to avoid.  Likewise, administrators of budgetary funding cannot move distributed funds from one recipient to another once they have been distributed.  As an alternative, investors may try to meet their target allocation incrementally through the investment of funds as they become available.  For a portfolio of stocks, this would mean purchasing more shares of investments that are below target values and not buying shares of invstments exceed target values.  portfolio_allocator optimizes this approach by calculating allotment amounts that will match the target allocation as much as possible in ultimate portfolio.

## How does it work?

portfolio_allocator calculates the difference between target and current values of investments (i.e., deficits) and the difference between current and target proportions (i.e., error).  These variables are then used to calculate allotment sets that will bring the ultimate composition of the portfolio closer to the target allocation provided by the user.  

Method 1 is the allocate_by_rank method.  This method allocates `cash` to eliminate the deficits in rank order until the `cash` is gone.  For example, if the `cash` is \\$3 and the two top ranking deficits are each \\$2, this method will result in an allocation of \\$2 to the top-ranking deficit and \\$1 to the subsequent deficit. In this example, the error for the first investment will be reduced to zero while the error for the remaining investments may still be significant.  

Method 2 is designed to minimize errors as much as possible for all investments with a deficit greater than zero.  However, Method 2, the allocate_for_minimal_errors method, can return impractical allocations when not needed. That is, when all error values for investments with deficits greater than zero are minimized by Method 1, Method 2 may return a set of allocations that includes negative numbers. To prevent this outcome, portfolio_allocator tests the error values produced by Method 1 before proceeding to Method 2.  If errors are minimized by Method 1, portfolio_allocator will not implement Method 2.  A detailed illustration of how each method works is provided in the supplementary notebook included in this repository.


## How do I use portfolio_allocator?
portfolio_allocator is a function written in python.  It can be imported using the py file in this repository.  The function returns a pandas DataFrame containing the results of the two methods.  To do this, portolio_allocator takes three arguments:
	- `cash` (integer, float) is the lump sum money to be allocated to investments.
	- `target_pcts` (iterable container of floats) are the set of target allocations specified as proportions that sum to 1 (minus rounding error)
	- `current_values` (iterable container of integers or floats) are the current values of the investments in the portfolio (or cumulative sum of distributions to funding recipients)

These parameters are used to create a pandas DataFrame with five calculated columns:
	- 'current%' is the proportion of the current value of investment in the portfolio
	- 'target_value' reflects the desired composition after `cash` has been distributed
	- 'deficit' is the target value minum the current value
	- 'error' is the difference between `target_pcts` and 'current%'
	- 'rank' is the rankings of deficits in decending order such that the largest deficit is assigned a rank of zero

### How to Interpret the Results
The final DataFrame returned by portfolio_allocator contains columns for `target_pcts`, `current_values` and each calculated column.  In addition, it contains columns for the allotment set generated by Method 1, 'allocate_by_rank', and the corresponding errors ('errors2') for hypothetical portfolio composition that would be achieved if the allocation set was implemented.  If required, the DataFrame will include columns for  the allocation set generated by Method 2, 'allocate_for_minimal_errors', and the corresponding errors ('errors3') for hypothetical portfolio composition that would be achieved if the allocation set was implemented.

### Want more Details?

To further illustrate the difference between each method, a notebook file is included in this repository.  Note that while the portfolio size and allotment amounts are relatively small in this illustration, the difference between optimal and suboptimal allotment sets may have significant consequences for larger portfolios with larger allocation amounts.
