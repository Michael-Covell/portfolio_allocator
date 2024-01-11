# portfolio_allocator

Calculate the optimal allotments of a lump sum to investments in a portfolio with a target allocation.  This may be used as an alternative to rebalancing.

## Description

portfolio_allocator is a user-defined function written in python.  It's purpose is to determine the best allocation of a lump sum to a portfolio.  Given a lump sum of cash and a set of target percentages, it calculates allotments that will render a portfolio matching a target allocation as closely as possible.  Depending on the allotment method, allotments are calculated based on the discrepancy between each investment’s current and target values (i.e., deficits) or the difference between current and target percentages (i.e., allocation error).  The allocate_by_rank method calculates allotments iteratively by allocating cash to eliminate the deficits in rank order until the cash is gone.  For example, if the cash is $3 and the two top ranking deficits are each $2, this method will result in an allocation of $2 to the top-ranking deficit and $1 to the subsequent deficit.  In contrast, the allocate_for_minimal_errors method minimizes allocation errors across investments as much as possible.  

An Apps Script file containing a custom function has been added to this repository to offer a Google Sheets implementation of the allocate_for_minimal_errors method.


### Dependencies

* portfolio_allocator requires pandas and numpy.

### Resources

* [Purpose and Uses of portfolio_allocator](purpose_and_uses.md)
* [A Guided Tour of portfolio_allocator](portfolio_allocator_tour.ipynb)
* [Custom Function in Apps Script for Google Sheets Implementation](allotment_calculator_custom_function.gs)
