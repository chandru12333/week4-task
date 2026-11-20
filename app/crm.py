
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create retry configuration
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

# Create reusable session
session = requests.Session()

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("http://", adapter)
session.mount("https://", adapter)


def get_customer_details(customer_id: int):

    url = f"http://127.0.0.1:8001/customers/{customer_id}"

    try:
        response = session.get(url, timeout=5)

        if response.status_code == 404:
            return {
                "error": f"Customer {customer_id} not found"
            }

        response.raise_for_status()

        return response.json()

    except requests.Timeout:
        return {
            "error": "CRM service timed out. Please try again."
        }

    except requests.RequestException:
        return {
            "error": "CRM service is unavailable. Please try again."
        }
