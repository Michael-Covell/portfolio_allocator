# portfolio_allocator

Optimize the distribution of funds to a portfolio of investments or budgetary funding recipients according to a corresponding set of target allocations.

## Description

portfolio_allocator is a user-defined function written in python.  Given a set of target allocations, current values of investments, and a cash value provided by the user, portfolio_allocator generates an allotment for each investment.  Allotment sets are calculated based on the discrepancy between each investment’s current and target values (i.e., deficits) or the difference between current and target allocations (i.e., error).  The allocate_by_rank method allocates cash to eliminate the deficits in rank order until the cash is gone.  For example, if the cash is $3 and the two top ranking deficits are each $2, this method will result in an allocation of $2 to the top-ranking deficit and $1 to the subsequent deficit. The allocate_for_minimal_errors method is designed to minimize errors as much as possible.  For a more detailed description of portfolio_allocator, its purposes, and functional components, please see the accompanying file, purpose_and_uses.md.  An illustration of how each method works is provided by the supplementary notebook included in this repository.

### Dependencies

* portfolio_allocator requires pandas and numpy.
