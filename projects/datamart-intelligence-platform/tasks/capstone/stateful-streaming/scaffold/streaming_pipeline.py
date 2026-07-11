from pyspark.sql import functions as F


def windowed_revenue(events):
    # This uses a 5-minute window (wrong) and no watermark.
    # TODO: 10-minute watermarked window summing amount -> window_start, revenue.
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "5 minutes"))
        .agg(F.sum("amount").alias("revenue"))
        .select(F.col("window.start").cast("string").alias("window_start"), "revenue")
    )


def active_users(events):
    # This counts ALL events, not DISTINCT users.
    # TODO: use F.approx_count_distinct("user") as active_users.
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.count("*").alias("active_users"))
        .select(F.col("window.start").cast("string").alias("window_start"), "active_users")
    )


def peak_window(events):
    # This returns EVERY window, not just the peak.
    # TODO: order by revenue descending and keep only the top window.
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .withWatermark("ts", "10 minutes")
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.sum("amount").alias("revenue"))
        .select(F.col("window.start").cast("string").alias("window_start"), "revenue")
    )
