# Bug report: conversion rate looks wrong

> "The conversion-rate tile shows `0.1` when it should be around `12.5%`. Off by
> a factor of 100."

## The buggy code

```python
def conversion_rate(conversions, visitors):
    return round(conversions / visitors, 1)   # <-- a ratio, not a percentage
```

`25 / 200 = 0.125`, rounded to `0.1`. The math isn't *wrong*, it's *incomplete*:
a **rate** is a ratio, but a **percentage** is that ratio times 100. The tile
expects a percentage, so the code is a factor of 100 short. This "forgot the
×100" bug is one of the most common in analytics code.

## The fix

```python
def conversion_rate(conversions, visitors):
    return round(conversions / visitors * 100, 1)
```

`25 / 200 * 100 = 12.5`.

## Your task

Fix `conversion_rate` in `conversion_rate.py` so it returns a percentage rounded
to one decimal. Expected: `conversion_rate(25, 200)` → `12.5`.
