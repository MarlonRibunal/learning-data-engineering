def partition_path(table, date):
    year, month, day = date.split("-")
    return f"{table}/year={year}/month={month}/day={day}"
