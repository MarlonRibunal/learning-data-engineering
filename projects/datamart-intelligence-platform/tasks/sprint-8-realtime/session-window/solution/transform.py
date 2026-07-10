from pyspark.sql import functions as F


def transform(events):
    return (
        events.withColumn("ts", F.to_timestamp("ts"))
        .groupBy(F.session_window("ts", "5 minutes"))
        .count()
        .select(
            F.col("session_window.start").cast("string").alias("session_start"),
            "count",
        )
    )
