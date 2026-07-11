def conversion_rate(conversions, visitors):
    # BUG: returns a ratio (0.125) instead of a percentage (12.5).
    return round(conversions / visitors, 1)
