from pyspark.sql import functions as F


def windowed_revenue(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.sum("amount").alias("revenue"))
        .select(F.col("window.start").cast("string").alias("window_start"), "revenue")
    )


def active_users(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.approx_count_distinct("user").alias("active_users"))
        .select(F.col("window.start").cast("string").alias("window_start"), "active_users")
    )


def peak_window(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.sum("amount").alias("revenue"))
        .orderBy(F.col("revenue").desc())
        .limit(1)
        .select(F.col("window.start").cast("string").alias("window_start"), "revenue")
    )
