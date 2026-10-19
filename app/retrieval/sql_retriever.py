from typing import Dict, Any


BUSINESS_METRICS = {
    "total_revenue": 1250000,
    "average_order_value": 142.75,
    "total_orders": 8760,
    "total_customers": 4320,
    "churn_rate": 0.184,
}


def retrieve_sql_context(query: str) -> Dict[str, Any]:
    query_lower = query.lower()

    results = {}

    if "revenue" in query_lower:
        results["total_revenue"] = BUSINESS_METRICS["total_revenue"]

    if "average order" in query_lower or "average" in query_lower:
        results["average_order_value"] = BUSINESS_METRICS["average_order_value"]

    if "orders" in query_lower or "order" in query_lower:
        results["total_orders"] = BUSINESS_METRICS["total_orders"]

    if "customers" in query_lower or "customer" in query_lower:
        results["total_customers"] = BUSINESS_METRICS["total_customers"]

    if "churn" in query_lower:
        results["churn_rate"] = BUSINESS_METRICS["churn_rate"]

    if not results:
        results = BUSINESS_METRICS.copy()

    return results