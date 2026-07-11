def consumer_lag(latest_offset, committed_offset):
    return latest_offset - committed_offset
