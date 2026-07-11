from pyspark.sql import functions as F


def transform(orders):
    # TODO: groupBy customer_id, pivot on category, sum amount, and fillna(0).
    return orders
