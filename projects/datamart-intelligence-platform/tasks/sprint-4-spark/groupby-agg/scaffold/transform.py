from pyspark.sql import functions as F


def transform(orders):
    # TODO: return one row per category with a `revenue` column that sums
    # `amount`. Use orders.groupBy(...).agg(F.sum(...).alias("revenue")).
    return orders
