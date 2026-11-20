
import requests
import time

API_URL = "http://127.0.0.1:8000/chat"

scenarios = [
    {
        "name": "Document Q1",
        "question": "What topics are covered in Week 3?",
        "expected": "week 3",
        "tool": "ChromaDB"
    },
    {
        "name": "Document Q2",
        "question": "Explain neural networks.",
        "expected": "neural",
        "tool": "ChromaDB"
    },
    {
        "name": "Document Q3",
        "question": "What is backpropagation?",
        "expected": "backpropagation",
        "tool": "ChromaDB"
    },
    {
        "name": "Unanswerable Q1",
        "question": "What is the CEO's home address?",
        "expected": "i don't know",
        "tool": "None"
    },
    {
        "name": "Unanswerable Q2",
        "question": "What is the weather on Mars tomorrow?",
        "expected": "i don't know",
        "tool": "None"
    },
    {
        "name": "CRM Q1",
        "question": "What are the details of customer 3?",
        "expected": "customer",
        "tool": "CRM"
    },
    {
        "name": "CRM Q2",
        "question": "What plan is customer 3 subscribed to?",
        "expected": "standard",
        "tool": "CRM"
    },
    {
        "name": "Order Q1",
        "question": "What is the status of order 1048?",
        "expected": "1048",
        "tool": "PostgreSQL"
    },
    {
        "name": "Order Q2",
        "question": "Show all orders for customer 3.",
        "expected": "order",
        "tool": "PostgreSQL"
    },
    {
        "name": "Email Draft",
        "question": "Draft an email to customer 3 about the status of order 1048.",
        "expected": "subject",
        "tool": "CRM + PostgreSQL + Email draft"
    }
]

results = []

for scenario in scenarios:

    start = time.time()

    try:
        response = requests.post(
            API_URL,
            json={
                "message": scenario["question"],
                "session_id": "week4_testing"
            },
            timeout=60
        )

        elapsed = round(time.time() - start, 2)

        if response.status_code == 200:
            answer = response.json()["answer"]

            passed = scenario["expected"].lower() in answer.lower()

            status = "PASS" if passed else "FAIL"

        else:
            answer = response.text
            status = "FAIL"

        results.append({
            "Scenario": scenario["name"],
            "Result": status,
            "Response Time": elapsed,
            "Tool": scenario["tool"],
            "Answer": answer
        })

    except Exception as error:

        results.append({
            "Scenario": scenario["name"],
            "Result": "FAIL",
            "Response Time": "N/A",
            "Tool": scenario["tool"],
            "Answer": str(error)
        })


print("\n========== END-TO-END TEST REPORT ==========\n")

for result in results:
    print(result)

passed = sum(1 for r in results if r["Result"] == "PASS")
failed = len(results) - passed

print("\n========== SUMMARY ==========")
print("Total:", len(results))
print("Passed:", passed)
print("Failed:", failed)
