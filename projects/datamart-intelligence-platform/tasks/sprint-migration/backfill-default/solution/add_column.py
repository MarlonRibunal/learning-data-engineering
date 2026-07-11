def add_column(rows, column, default):
    return [{**row, column: row.get(column, default)} for row in rows]
