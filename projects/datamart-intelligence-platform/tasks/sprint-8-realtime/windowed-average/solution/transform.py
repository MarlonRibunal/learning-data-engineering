from pyspark.sql import functions as F


def transform(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.round(F.avg("amount"), 2).alias("avg_amount"))
        .select(F.col("window.start").cast("string").alias("window_start"), "avg_amount")
    )
