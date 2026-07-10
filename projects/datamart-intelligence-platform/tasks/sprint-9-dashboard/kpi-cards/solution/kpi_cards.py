def kpi_cards(rows):
    total = sum(r["amount"] for r in rows)
    count = len(rows)
    return {
        "total_revenue": total,
        "order_count": count,
        "avg_order_value": round(total / count, 2) if count else 0,
    }
