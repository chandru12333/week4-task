
from app.services.order_db import get_db_connection


# Tool 1: Get one order's status
def get_order_status(order_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT order_id, customer_id, order_status,
               delivery_status, shipped_date, total_amount
        FROM orders
        WHERE order_id = %s
        """,
        (order_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        return {"error": "Order not found"}

    return {
        "order_id": result[0],
        "customer_id": result[1],
        "order_status": result[2],
        "delivery_status": result[3],
        "shipped_date": str(result[4]) if result[4] else None,
        "total_amount": float(result[5])
    }


# Tool 2: Get all orders for one customer
def get_customer_orders(customer_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT order_id, order_date, order_status,
               delivery_status, total_amount
        FROM orders
        WHERE customer_id = %s
        ORDER BY order_date DESC
        """,
        (customer_id,)
    )

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "order_id": row[0],
            "order_date": str(row[1]),
            "order_status": row[2],
            "delivery_status": row[3],
            "total_amount": float(row[4])
        }
        for row in results
    ]
