"""
Data quality layer for TDM.
Defines DQ check classes and domain-specific rule sets.
Results are persisted to a Delta table for auditability and lineage.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType
from databricks.src.utils import table_name


@dataclass
class DQResult:
    check_name:  str
    domain:      str
    column:      str
    passed:      bool
    score:       float   # 0.0 – 1.0
    details:     str
    run_id:      str
    checked_at:  str


# ── Check classes ─────────────────────────────────────────────────────────────

class CompletenessCheck:
    """Fails if null rate exceeds (1 - threshold)."""

    def __init__(self, column: str, threshold: float = 0.95):
        self.column = column
        self.threshold = threshold

    def run(self, df: DataFrame, domain: str, run_id: str) -> DQResult:
        total    = df.count()
        non_null = df.filter(F.col(self.column).isNotNull()).count()
        score    = non_null / total if total > 0 else 0.0
        return DQResult(
            check_name="completeness",
            domain=domain,
            column=self.column,
            passed=score >= self.threshold,
            score=round(score, 4),
            details=f"{non_null}/{total} non-null",
            run_id=run_id,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )


class UniquenessCheck:
    """Fails if any duplicate values exist in the column."""

    def __init__(self, column: str):
        self.column = column

    def run(self, df: DataFrame, domain: str, run_id: str) -> DQResult:
        total    = df.count()
        distinct = df.select(self.column).distinct().count()
        score    = distinct / total if total > 0 else 0.0
        return DQResult(
            check_name="uniqueness",
            domain=domain,
            column=self.column,
            passed=(distinct == total),
            score=round(score, 4),
            details=f"{distinct} distinct / {total} total",
            run_id=run_id,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )


class ValidityCheck:
    """Fails if the proportion of rows matching the regex is below threshold."""

    def __init__(self, column: str, pattern: str, threshold: float = 0.95):
        self.column = column
        self.pattern = pattern
        self.threshold = threshold

    def run(self, df: DataFrame, domain: str, run_id: str) -> DQResult:
        total = df.count()
        valid = df.filter(F.col(self.column).rlike(self.pattern)).count()
        score = valid / total if total > 0 else 0.0
        return DQResult(
            check_name="validity",
            domain=domain,
            column=self.column,
            passed=score >= self.threshold,
            score=round(score, 4),
            details=f"{valid}/{total} match pattern '{self.pattern}'",
            run_id=run_id,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )


# ── Domain rule registry ──────────────────────────────────────────────────────

DQ_RULES: dict[str, list] = {
    "customer": [
        CompletenessCheck("customer_id"),
        CompletenessCheck("email"),
        UniquenessCheck("customer_id"),
        ValidityCheck("email", r"^[^@]+@[^@]+\.[^@]+$"),
    ],
    "order": [
        CompletenessCheck("order_id"),
        CompletenessCheck("customer_id"),
        CompletenessCheck("order_date"),
        UniquenessCheck("order_id"),
    ],
    "product": [
        CompletenessCheck("product_id"),
        CompletenessCheck("name"),
        UniquenessCheck("product_id"),
    ],
    "payment": [
        CompletenessCheck("payment_id"),
        CompletenessCheck("order_id"),
        CompletenessCheck("amount"),
        CompletenessCheck("status"),
        UniquenessCheck("payment_id"),
        ValidityCheck("status", r"^(CAPTURED|REFUNDED|DECLINED|PENDING)$"),
        ValidityCheck("amount", r"^\d+(\.\d+)?$"),
    ],
}


# ── Runner and persistence ────────────────────────────────────────────────────

def run_dq_checks(df: DataFrame, domain: str, run_id: str) -> list[DQResult]:
    """Run all registered DQ checks for a domain. Returns results list."""
    return [rule.run(df, domain, run_id) for rule in DQ_RULES.get(domain, [])]


def write_dq_results(
    results: list[DQResult],
    spark: SparkSession,
    catalog: str,
    schema: str,
    table_format: str = "delta",
) -> None:
    """Persist DQ results to table and raise if any check failed."""
    rows = [vars(r) for r in results]
    df   = spark.createDataFrame(rows)
    table = table_name(catalog, schema, "dq_results")
    df.write.format(table_format).mode("append").option("mergeSchema", "true").saveAsTable(table)

    failed = [r for r in results if not r.passed]
    if failed:
        msgs = [f"{r.check_name}({r.column}) score={r.score}" for r in failed]
        raise ValueError(f"DQ checks failed [{results[0].domain}]: {msgs}")
