from pyspark.sql import functions as F


def transform(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.window("ts", "10 minutes"), "category")
        .agg(F.sum("amount").alias("revenue"))
        .select(
            F.col("window.start").cast("string").alias("window_start"),
            "category",
            "revenue",
        )
    )
