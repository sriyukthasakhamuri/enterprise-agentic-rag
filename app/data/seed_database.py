from app.data.database import (
    get_connection,
    initialize_database,
)


CUSTOMERS = [
    (
        1,
        "Acme Retail",
        "Enterprise",
        "active",
    ),
    (
        2,
        "Nova Health",
        "Enterprise",
        "active",
    ),
    (
        3,
        "BrightMart",
        "Mid-Market",
        "churned",
    ),
    (
        4,
        "Summit Foods",
        "Mid-Market",
        "active",
    ),
    (
        5,
        "Vertex Labs",
        "SMB",
        "churned",
    ),
]


ORDERS = [
    (
        1001,
        1,
        320000.00,
        0,
        "completed",
    ),
    (
        1002,
        1,
        180000.00,
        2,
        "completed",
    ),
    (
        1003,
        2,
        275000.00,
        1,
        "completed",
    ),
    (
        1004,
        2,
        125000.00,
        0,
        "completed",
    ),
    (
        1005,
        3,
        110000.00,
        6,
        "cancelled",
    ),
    (
        1006,
        3,
        65000.00,
        8,
        "cancelled",
    ),
    (
        1007,
        4,
        95000.00,
        3,
        "completed",
    ),
    (
        1008,
        4,
        45000.00,
        1,
        "completed",
    ),
    (
        1009,
        5,
        25000.00,
        7,
        "cancelled",
    ),
    (
        1010,
        5,
        10000.00,
        9,
        "cancelled",
    ),
]


def seed_database():
    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM orders
        """
    )

    cursor.execute(
        """
        DELETE FROM customers
        """
    )

    cursor.executemany(
        """
        INSERT INTO customers (
            customer_id,
            customer_name,
            segment,
            status
        )
        VALUES (?, ?, ?, ?)
        """,
        CUSTOMERS,
    )

    cursor.executemany(
        """
        INSERT INTO orders (
            order_id,
            customer_id,
            order_amount,
            delivery_delay_days,
            order_status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        ORDERS,
    )

    connection.commit()
    connection.close()

    print(
        "Database seeded successfully."
    )


if __name__ == "__main__":
    seed_database()