import sqlite3
from pathlib import Path


DATABASE_PATH = (
    Path(__file__).resolve().parent
    / "enterprise_analytics.db"
)


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            segment TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_amount REAL NOT NULL,
            delivery_delay_days INTEGER NOT NULL,
            order_status TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
        """
    )

    connection.commit()
    connection.close()