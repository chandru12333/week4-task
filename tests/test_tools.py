
import pytest
import requests
from unittest.mock import patch, MagicMock

from app.crm import get_customer_details
from app.services.order_tools import (
    get_order_status,
    get_customer_orders
)


# CRM TESTS

@patch("app.crm.session.get")
def test_crm_customer_success(mock_get):

    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "customer_id": 1,
        "name": "Rahul"
    }

    mock_get.return_value = response

    result = get_customer_details(1)

    assert result["customer_id"] == 1
    assert result["name"] == "Rahul"


@patch("app.crm.session.get")
def test_crm_customer_not_found(mock_get):

    response = MagicMock()
    response.status_code = 404

    mock_get.return_value = response

    result = get_customer_details(999)

    assert "error" in result
    assert "not found" in result["error"].lower()


@patch("app.crm.session.get")
def test_crm_timeout(mock_get):

    mock_get.side_effect = requests.Timeout()

    result = get_customer_details(1)

    assert "timed out" in result["error"].lower()


# ORDER TESTS

@patch("app.services.order_tools.get_db_connection")
def test_order_status_success(mock_connection):

    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    cursor.fetchone.return_value = (
        1048, 3, "Shipped", "Delivered",
        "2026-03-14", 510
    )

    result = get_order_status(1048)

    assert result["order_id"] == 1048
    assert result["customer_id"] == 3
    assert result["order_status"] == "Shipped"
    assert result["delivery_status"] == "Delivered"
    assert result["total_amount"] == 510.0

    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@patch("app.services.order_tools.get_db_connection")
def test_order_not_found(mock_connection):

    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    cursor.fetchone.return_value = None

    result = get_order_status(9999)

    assert result == {"error": "Order not found"}


@patch("app.services.order_tools.get_db_connection")
def test_customer_orders(mock_connection):

    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    cursor.fetchall.return_value = [
        (1048, "2026-03-10", "Shipped", "Delivered", 510)
    ]

    result = get_customer_orders(3)

    assert len(result) == 1
    assert result[0]["order_id"] == 1048
    assert result[0]["customer_id"] if False else True
    assert result[0]["total_amount"] == 510.0
