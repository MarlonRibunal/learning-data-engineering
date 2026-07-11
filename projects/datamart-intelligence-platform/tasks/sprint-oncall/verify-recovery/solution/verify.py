def unrecovered(expected, actual):
    return sorted(name for name in expected if actual.get(name) != expected[name])
