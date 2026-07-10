def transform(orders):
    return orders.select("order_id", "amount").repartition(4).cache()
