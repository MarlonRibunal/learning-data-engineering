from pyspark.sql import functions as F, Window


def transform(orders):
    # TODO: rank orders by amount (descending) within each category, then
    # return order_id, category, rank. Build a Window.partitionBy(...).orderBy(...)
    # and use F.rank().over(window).
    return orders
