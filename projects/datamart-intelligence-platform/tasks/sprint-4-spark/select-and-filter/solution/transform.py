def transform(orders):
    return orders.filter(orders.amount >= 50).select("order_id", "amount")
