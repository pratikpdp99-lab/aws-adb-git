"""
Synthetic data generation for lower environments.
Generates statistically similar but fully fake records for a given domain schema.
"""

import random
import string
import uuid
from datetime import date, timedelta
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType


def random_string(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    return f"{random_string(6)}@{random_string(4)}.com"


def random_date(start_year: int = 2020) -> str:
    start = date(start_year, 1, 1)
    delta = timedelta(days=random.randint(0, 1000))
    return str(start + delta)


# Domain-specific row generators — extend per schema
_GENERATORS = {
    "customer": lambda: {
        "customer_id": f"CUST-{random.randint(100000, 999999)}",
        "first_name":  random_string(6).capitalize(),
        "last_name":   random_string(8).capitalize(),
        "email":       random_email(),
        "phone":       f"+1-{random.randint(200,999)}-{random.randint(1000000,9999999)}",
        "created_date": random_date(),
    },
    "order": lambda: {
        "order_id":    f"ORD-{random.randint(100000, 999999)}",
        "customer_id": f"CUST-{random.randint(100000, 999999)}",
        "order_date":  random_date(),
        "total_amount": round(random.uniform(10.0, 500.0), 2),
        "status":      random.choice(["PLACED", "SHIPPED", "DELIVERED", "CANCELLED"]),
    },
    "payment": lambda: {
        "payment_id":     str(uuid.uuid4()),
        "order_id":       f"ORD-{random.randint(100000, 999999)}",
        "customer_id":    f"CUST-{random.randint(100000, 999999)}",
        "payment_method": random.choice(["credit_card", "debit_card", "paypal", "apple_pay", "gift_card"]),
        "card_last4":     str(random.randint(1000, 9999)),
        "card_network":   random.choice(["VISA", "MASTERCARD", "AMEX", "DISCOVER"]),
        "amount":         round(random.uniform(10.0, 500.0), 2),
        "currency":       "USD",
        "status":         random.choice(["CAPTURED", "REFUNDED", "DECLINED", "PENDING"]),
        "gateway":        random.choice(["stripe", "braintree", "adyen", "paypal"]),
        "created_at":     random_date(2022),
    },
}


def generate(domain: str, n: int, spark: SparkSession) -> DataFrame:
    """Generate n synthetic rows for the given domain."""
    generator = _GENERATORS.get(domain)
    if not generator:
        raise ValueError(f"No synthetic generator defined for domain: {domain}")
    rows = [generator() for _ in range(n)]
    return spark.createDataFrame(rows)
