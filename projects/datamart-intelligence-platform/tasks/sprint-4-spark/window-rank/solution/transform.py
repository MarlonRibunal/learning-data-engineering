from pyspark.sql import functions as F, Window


def transform(orders):
    w = Window.partitionBy("category").orderBy(F.col("amount").desc())
    return (
        orders.withColumn("rank", F.rank().over(w))
        .select("order_id", "category", "rank")
    )
