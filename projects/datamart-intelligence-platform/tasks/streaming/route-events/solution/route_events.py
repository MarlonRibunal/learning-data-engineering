def assign_partitions(events, num_partitions):
    return [event["customer_id"] % num_partitions for event in events]
