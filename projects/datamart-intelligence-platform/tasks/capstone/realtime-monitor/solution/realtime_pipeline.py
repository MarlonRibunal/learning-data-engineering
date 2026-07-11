from pyspark.sql import functions as F


def clean(events):
    return events.filter(F.col("amount") > 0).select("ts", "category", "amount")


def windowed_revenue(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.sum("amount").alias("revenue"))
        .select(F.col("window.start").cast("string").alias("window_start"), "revenue")
    )


def busiest_window(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.sum("amount").alias("revenue"))
        .orderBy(F.col("revenue").desc())
        .limit(1)
        .select(F.col("window.start").cast("string").alias("window_start"), "revenue")
    )
