from pyspark.sql import functions as F


def transform(orders):
    return orders.groupBy("category").agg(F.sum("amount").alias("revenue"))
