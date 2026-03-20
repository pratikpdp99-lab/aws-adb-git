"""
Sensitive data masking and tokenization.
Applies masking rules to PII fields before writing to Silver layer.
"""

import hashlib
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType


# PII fields per domain — extend as needed
PII_FIELDS = {
    "customer": ["email", "phone", "ssn", "first_name", "last_name", "address"],
    "order":    ["customer_id", "billing_address", "shipping_address"],
    "loyalty":  ["customer_id", "email"],
}


def hash_column(df: DataFrame, col_name: str) -> DataFrame:
    """Replace column value with SHA-256 hash (deterministic tokenization)."""
    hash_udf = F.udf(
        lambda val: hashlib.sha256(val.encode()).hexdigest() if val else None,
        StringType(),
    )
    return df.withColumn(col_name, hash_udf(F.col(col_name)))


def mask_column(df: DataFrame, col_name: str, mask: str = "***MASKED***") -> DataFrame:
    """Replace column value with a static mask."""
    return df.withColumn(col_name, F.lit(mask))


def apply_masking(df: DataFrame, domain: str, strategy: str = "hash") -> DataFrame:
    """
    Apply masking to all PII fields for a given domain.
    strategy: 'hash' (tokenize) | 'mask' (redact)
    """
    fields = PII_FIELDS.get(domain, [])
    existing = [f.name for f in df.schema.fields]
    for field in fields:
        if field not in existing:
            continue
        if strategy == "hash":
            df = hash_column(df, field)
        else:
            df = mask_column(df, field)
    return df
