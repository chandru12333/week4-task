
from fastapi import FastAPI, HTTPException

app = FastAPI()

customers = {
    1: {
        "name": "Arun",
        "plan": "Basic",
        "email": "arun@gmail.com",
        "city": "Chennai"
    },
    2: {
        "name": "Priya",
        "plan": "Premium",
        "email": "priya@gmail.com",
        "city": "Coimbatore"
    },
    3: {
        "name": "Rahul",
        "plan": "Standard",
        "email": "rahul@gmail.com",
        "city": "Bangalore"
    },
    4: {
        "name": "Divya",
        "plan": "Basic",
        "email": "divya@gmail.com",
        "city": "Madurai"
    },
    5: {
        "name": "Karthik",
        "plan": "Premium",
        "email": "karthik@gmail.com",
        "city": "Chennai"
    }
}

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):

    if customer_id not in customers:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customers[customer_id]
