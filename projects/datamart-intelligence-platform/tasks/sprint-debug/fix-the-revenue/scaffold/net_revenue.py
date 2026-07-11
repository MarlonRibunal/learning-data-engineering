def net_revenue(orders):
    # BUG: counts refunded orders as revenue, inflating the total.
    return sum(o["amount"] for o in orders)
