def merge(target, updates, key):
    by_key = {row[key]: row for row in target}
    for update in updates:
        by_key[update[key]] = update
    return [by_key[k] for k in sorted(by_key)]
