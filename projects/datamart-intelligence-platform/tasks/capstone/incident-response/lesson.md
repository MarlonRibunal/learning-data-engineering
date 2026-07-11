# Capstone: the Incident Response Gauntlet

A capstone for everything you drilled in the On-Call, Debug, and Migration
tracks — run as **one incident, end to end**. A production alert just fired.
You'll write **one file** with four functions, each a stage of the playbook, and
passing all four emits an **incident-report portfolio artifact**.

## The playbook

```
🔔 alert ──detect──▶ breached tables ──diagnose──▶ root-cause job ──quantify──▶ $ impact ──verify──▶ recovered?
```

### `breached_tables(tables, sla_minutes)` — detect
Return the sorted names of tables older than the SLA. `tables` is a list of
`{"name", "age_min"}`.

### `root_cause(runs)` — diagnose
Return the name of the **first** failed job (its downstream failures are
victims). `runs` is `{"job", "status"}` in execution order.

### `revenue_impact(orders)` — quantify
How much did the bug overstate revenue? Return the difference between the naive
total (all orders) and the correct total (excluding `refunded`). That's the
number leadership asks for first.

```python
def revenue_impact(orders):
    naive   = sum(o["amount"] for o in orders)
    correct = sum(o["amount"] for o in orders if o["status"] != "refunded")
    return naive - correct
```

### `is_recovered(expected, actual)` — verify
Return `True` only if **every** table's actual count matches expected — i.e. the
incident can be closed. `all(...)` is your friend here.

## Your task

Fill in all four functions in `incident_response.py`. Together they *are* the
incident response — detect, diagnose, quantify, verify. Pass all four to earn
the artifact.
