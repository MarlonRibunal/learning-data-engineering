# Bug report: revenue is overstated

> "Finance says our revenue number is too high. We think refunded orders are
> being counted as sales."

## The buggy code

```python
def net_revenue(orders):
    return sum(o["amount"] for o in orders)   # <-- sums EVERY order, refunds included
```

`net_revenue` sums the `amount` of every order regardless of `status`. A
refunded order isn't revenue — its money went back to the customer — so counting
it inflates the total. With a $30 refund in the mix, the number is $30 too high.

## The fix

Net revenue = paid orders minus refunds. The simplest correct version just
excludes refunded orders from the sum:

```python
def net_revenue(orders):
    return sum(o["amount"] for o in orders if o["status"] != "refunded")
```

## Your task

Fix `net_revenue` in `net_revenue.py` so refunded orders don't count. Expected:
`100 + 50 = 150` (the `30` refund excluded).
