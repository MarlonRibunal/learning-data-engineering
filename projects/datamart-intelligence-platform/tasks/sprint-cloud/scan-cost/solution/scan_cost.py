def scan_cost(bytes_scanned, price_per_tb):
    terabytes = bytes_scanned / 1e12
    return round(terabytes * price_per_tb, 2)
