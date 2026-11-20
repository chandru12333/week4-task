
import json
import re
import ollama

from app.crm import get_customer_details
from app.services.order_tools import (
    get_order_status,
    get_customer_orders
)


# Existing LLM function for PDF-based RAG
def generate_answer(prompt):

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# CRM tool definition
crm_tool = {
    "type": "function",
    "function": {
        "name": "get_customer_details",
        "description": "Get customer details from CRM using customer ID",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The customer ID"
                }
            },
            "required": ["customer_id"]
        }
    }
}


# LLM decides whether to call CRM
def generate_answer_with_crm_tool(prompt):

    # Only consider CRM when a customer ID is mentioned
    if not re.search(
        r"\bcustomer\s+(?:id\s*)?#?\s*\d+\b",
        prompt,
        re.IGNORECASE
    ):
        return None

    messages = [
        {
            "role": "system",
            "content": """
            You are a CRM assistant.

            Use get_customer_details when the user asks
            about a specific customer's information.

            Examples:
            - Which plan is customer 3 on?
            - What is customer 2's email?
            - Which city does customer 5 live in?

            Never invent customer information.
            Always use the CRM tool for customer details.
            """
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    # Ask LLM to decide whether to call CRM
    response = ollama.chat(
        model="llama3.2",
        messages=messages,
        tools=[crm_tool]
    )

    tool_calls = response.message.tool_calls

    # No CRM tool required
    if not tool_calls:
        return None

    # Add LLM tool-call response
    messages.append(response.message)

    # Execute CRM tool
    for tool_call in tool_calls:

        if tool_call.function.name == "get_customer_details":

            args = tool_call.function.arguments

            result = get_customer_details(
                int(args["customer_id"])
            )

            messages.append({
                "role": "tool",
                "tool_name": "get_customer_details",
                "content": json.dumps(result)
            })

    # Generate final answer
    final_response = ollama.chat(
        model="llama3.2",
        messages=messages
    )

    return final_response.message.content


# PostgreSQL order tool definitions
order_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get order status using an order ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_orders",
            "description": "Get all orders for a customer using customer ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer"
                    }
                },
                "required": ["customer_id"]
            }
        }
    }
]


def generate_answer_with_order_tools(prompt):

    # Only process questions about orders
    if not re.search(
        r"\border\s+#?\d+\b",
        prompt,
        re.IGNORECASE
    ) and not re.search(
        r"\borders?\b.*\bcustomer\s+(?:id\s*)?#?\s*\d+\b|\bcustomer\s+(?:id\s*)?#?\s*\d+\b.*\borders?\b",
        prompt,
        re.IGNORECASE
    ):
        return None

    messages = [
        {
            "role": "system",
            "content": """
            You are an order assistant.

            Use get_order_status for a specific order.
            Use get_customer_orders for a customer's orders.

            Never write SQL.
            Never invent order information.
            Always use the available tools.
            """
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = ollama.chat(
        model="llama3.2",
        messages=messages,
        tools=order_tools
    )

    tool_calls = response.message.tool_calls

    if not tool_calls:
        return None

    messages.append(response.message)

    for tool_call in tool_calls:

        name = tool_call.function.name
        args = tool_call.function.arguments

        if name == "get_order_status":
            result = get_order_status(
                int(args["order_id"])
            )

        elif name == "get_customer_orders":
            result = get_customer_orders(
                int(args["customer_id"])
            )

        else:
            continue

        messages.append({
            "role": "tool",
            "tool_name": name,
            "content": json.dumps(result)
        })

    final_response = ollama.chat(
        model="llama3.2",
        messages=messages
    )

    return final_response.message.content
