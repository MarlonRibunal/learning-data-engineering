from pyspark.sql import functions as F


def transform(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "10 minutes"))
        .agg(F.countDistinct("category").alias("categories"))
        .select(F.col("window.start").cast("string").alias("window_start"), "categories")
    )
