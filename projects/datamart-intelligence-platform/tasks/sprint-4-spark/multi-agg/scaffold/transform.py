from pyspark.sql import functions as F


def transform(orders):
    # TODO: groupBy category and return order_count (count), revenue (sum),
    # and avg_amount (avg rounded to 2) in one .agg(...).
    return orders
