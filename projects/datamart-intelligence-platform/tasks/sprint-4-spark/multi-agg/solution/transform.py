from pyspark.sql import functions as F


def transform(orders):
    return orders.groupBy("category").agg(
        F.count("*").alias("order_count"),
        F.sum("amount").alias("revenue"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
    )
