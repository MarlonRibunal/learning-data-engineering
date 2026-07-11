def transform(orders):
    return orders.groupBy("customer_id").pivot("category").sum("amount").fillna(0)
