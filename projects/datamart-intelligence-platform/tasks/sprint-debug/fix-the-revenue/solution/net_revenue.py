def net_revenue(orders):
    return sum(o["amount"] for o in orders if o["status"] != "refunded")
