def transform(orders):
    # TODO: return only `order_id` and `amount`, spread across 4 partitions
    # and cached. Use .select(...).repartition(4).cache().
    return orders
