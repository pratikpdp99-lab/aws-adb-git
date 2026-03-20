"""Unit tests for synthetic.py."""

import pytest
from pyspark.sql import SparkSession
from databricks.src.synthetic import generate


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local").appName("tdm-test-synth").getOrCreate()


def test_generate_customer(spark):
    df = generate("customer", 10, spark)
    assert df.count() == 10
    assert "customer_id" in df.columns
    assert "email" in df.columns


def test_generate_order(spark):
    df = generate("order", 5, spark)
    assert df.count() == 5
    assert "order_id" in df.columns


def test_generate_unknown_domain(spark):
    with pytest.raises(ValueError):
        generate("unknown_domain", 5, spark)
