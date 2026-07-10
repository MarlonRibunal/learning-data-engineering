def transform(orders, customers):
    return orders.join(customers, on="customer_id").select(
        "order_id", "name", "amount"
    )
