def rename_keys(rows, mapping):
    return [{mapping.get(k, k): v for k, v in row.items()} for row in rows]
