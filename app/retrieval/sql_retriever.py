from typing import Dict, Any

from app.data.database import get_connection


def retrieve_sql_context(
    query: str,
) -> Dict[str, Any]:

    query_lower = query.lower()

    connection = get_connection()
    cursor = connection.cursor()

    results: Dict[str, Any] = {}

    if (
        "revenue" in query_lower
        or "sales" in query_lower
        or "total" in query_lower
    ):
        cursor.execute(
            """
            SELECT
                SUM(order_amount) AS total_revenue
            FROM orders
            WHERE order_status = 'completed'
            """
        )

        row = cursor.fetchone()

        results["total_revenue"] = (
            row["total_revenue"]
            if row
            else 0
        )

    if (
        "average order" in query_lower
        or "average order value" in query_lower
        or "aov" in query_lower
    ):
        cursor.execute(
            """
            SELECT
                AVG(order_amount)
                AS average_order_value
            FROM orders
            WHERE order_status = 'completed'
            """
        )

        row = cursor.fetchone()

        results["average_order_value"] = (
            round(
                row["average_order_value"],
                2,
            )
            if row
            and row["average_order_value"]
            is not None
            else 0
        )

    if (
        "order" in query_lower
        and "how many" in query_lower
    ) or (
        "total orders" in query_lower
    ):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_orders
            FROM orders
            """
        )

        row = cursor.fetchone()

        results["total_orders"] = (
            row["total_orders"]
            if row
            else 0
        )

    if (
        "customer" in query_lower
        and "how many" in query_lower
    ) or (
        "total customers" in query_lower
    ):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_customers
            FROM customers
            """
        )

        row = cursor.fetchone()

        results["total_customers"] = (
            row["total_customers"]
            if row
            else 0
        )

    if "churn" in query_lower:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_customers,
                SUM(
                    CASE
                        WHEN status = 'churned'
                        THEN 1
                        ELSE 0
                    END
                ) AS churned_customers
            FROM customers
            """
        )

        row = cursor.fetchone()

        total_customers = (
            row["total_customers"]
            if row
            else 0
        )

        churned_customers = (
            row["churned_customers"]
            if row
            else 0
        )

        churn_rate = (
            churned_customers
            / total_customers
            if total_customers
            else 0
        )

        results["churn_rate"] = round(
            churn_rate,
            3,
        )

    if (
        "delivery delay" in query_lower
        or "delivery delays" in query_lower
        or "late delivery" in query_lower
    ):
        cursor.execute(
            """
            SELECT
                AVG(delivery_delay_days)
                AS average_delivery_delay
            FROM orders
            """
        )

        row = cursor.fetchone()

        results[
            "average_delivery_delay_days"
        ] = (
            round(
                row["average_delivery_delay"],
                2,
            )
            if row
            and row["average_delivery_delay"]
            is not None
            else 0
        )

    if not results:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_orders,
                SUM(
                    CASE
                        WHEN order_status = 'completed'
                        THEN order_amount
                        ELSE 0
                    END
                ) AS total_revenue,
                AVG(order_amount)
                AS average_order_value,
                AVG(delivery_delay_days)
                AS average_delivery_delay
            FROM orders
            """
        )

        row = cursor.fetchone()

        results = {
            "total_orders":
                row["total_orders"],
            "total_revenue":
                row["total_revenue"],
            "average_order_value":
                round(
                    row["average_order_value"],
                    2,
                ),
            "average_delivery_delay_days":
                round(
                    row["average_delivery_delay"],
                    2,
                ),
        }

    connection.close()

    return results