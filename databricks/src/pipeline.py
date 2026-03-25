"""
TDM full pipeline orchestrator.
Flow: read source → write Bronze → DQ checks → transform to Silver → register in Unity Catalog

Usage (Databricks job / local):
    python -m databricks.src.pipeline \
        --catalog tdm_catalog --schema tdm_dev \
        --s3-bucket tdm-deckers-staged-dev

Usage (import):
    from databricks.src.pipeline import run_pipeline
    run_pipeline(spark, s3_paths={...}, catalog="tdm_catalog", schema="tdm_dev")
"""

import argparse
import uuid

from pyspark.sql import SparkSession

from databricks.src.ingest    import read_source, write_to_bronze, SUPPORTED_DOMAINS
from databricks.src.transform  import bronze_to_silver, write_silver
from databricks.src.quality    import run_dq_checks, write_dq_results
from databricks.src.catalog    import register_all
from databricks.src.utils      import table_name

PIPELINE_DOMAINS = ["customer", "order", "product"]


def run_pipeline(
    spark: SparkSession,
    s3_paths: dict[str, str],
    catalog: str = "tdm_catalog",
    schema: str = "tdm_dev",
    skip_dq_fail: bool = False,
    skip_catalog: bool = False,
    table_format: str = "delta",
) -> str:
    """
    Run the full TDM ingest + DQ + transform pipeline.

    Args:
        spark:        Active SparkSession.
        s3_paths:     {domain: path} — S3 URIs or local paths for testing.
        catalog:      Unity Catalog name.
        schema:       Schema / database name inside the catalog.
        skip_dq_fail: If True, log DQ failures but don't abort the pipeline.
        skip_catalog: If True, skip Unity Catalog registration (useful for local tests).

    Returns:
        run_id (str): UUID for this pipeline run, stamped on every Silver row.
    """
    run_id = str(uuid.uuid4())
    print(f"\n{'='*60}")
    print(f"TDM Pipeline  run_id={run_id}")
    print(f"catalog={catalog}  schema={schema}")
    print(f"{'='*60}\n")

    for domain in PIPELINE_DOMAINS:
        path = s3_paths.get(domain)
        if not path:
            print(f"[{domain}] SKIP — no path provided")
            continue

        # ── 1. Ingest → Bronze ────────────────────────────────────────────
        print(f"[{domain}] 1/3  Ingest  {path}")
        df = read_source(spark, path, format="csv")
        write_to_bronze(df, catalog, schema, domain, table_format=table_format)

        # ── 2. DQ checks ──────────────────────────────────────────────────
        print(f"[{domain}] 2/3  DQ checks")
        bronze_df = spark.table(table_name(catalog, schema, f"bronze_{domain}"))
        results   = run_dq_checks(bronze_df, domain, run_id)

        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        print(f"         {len(passed)} passed  {len(failed)} failed")
        for r in failed:
            print(f"         FAIL  {r.check_name}({r.column})  score={r.score}  {r.details}")

        write_dq_results(results, spark, catalog, schema, table_format=table_format)   # always persist

        if failed and not skip_dq_fail:
            msgs = [f"{r.check_name}({r.column})" for r in failed]
            raise RuntimeError(f"DQ failed for '{domain}' — aborting pipeline: {msgs}")

        # ── 3. Transform → Silver ─────────────────────────────────────────
        print(f"[{domain}] 3/3  Transform → Silver")
        silver_df = bronze_to_silver(bronze_df, domain, run_id=run_id)
        write_silver(silver_df, catalog, schema, domain, table_format=table_format)

    # ── 4. Unity Catalog registration ─────────────────────────────────────
    if not skip_catalog:
        print("\n[catalog] Registering tables in Unity Catalog")
        register_all(spark, catalog, schema)

    print(f"\nPipeline complete.  run_id={run_id}\n")
    return run_id


# ── CLI entry point (Databricks job) ─────────────────────────────────────────

def _parse_args():
    p = argparse.ArgumentParser(description="TDM pipeline")
    p.add_argument("--catalog",    default="tdm_catalog")
    p.add_argument("--schema",     default="tdm_dev")
    p.add_argument("--s3-bucket",  default="tdm-deckers-staged-dev")
    p.add_argument("--skip-dq-fail",  action="store_true")
    p.add_argument("--skip-catalog",  action="store_true")
    # AWS credentials — used on Databricks serverless where no instance profile exists
    p.add_argument("--aws-access-key-id",     default="")
    p.add_argument("--aws-secret-access-key", default="")
    p.add_argument("--aws-region",            default="us-east-1")
    return p.parse_args()


def _configure_s3(spark: SparkSession) -> None:
    """
    Configure S3A credentials from environment variables when running on
    Databricks serverless (no instance profile).  No-op if already configured
    via an instance profile or Unity Catalog external location.
    """
    import os
    access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    secret_key  = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    region      = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION", "us-east-1")
    if access_key and secret_key:
        spark.conf.set("spark.hadoop.fs.s3a.access.key",            access_key)
        spark.conf.set("spark.hadoop.fs.s3a.secret.key",            secret_key)
        spark.conf.set("spark.hadoop.fs.s3a.endpoint.region",       region)
        spark.conf.set("spark.hadoop.fs.s3a.aws.credentials.provider",
                       "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
        spark.conf.set("spark.hadoop.fs.s3a.impl",
                       "org.apache.hadoop.fs.s3a.S3AFileSystem")
        print(f"[s3] Configured S3A credentials from environment (region={region})")


if __name__ == "__main__":
    args = _parse_args()
    spark = SparkSession.builder.appName("tdm-pipeline").getOrCreate()
    # Inject CLI-supplied credentials into env so _configure_s3 picks them up
    import os
    if args.aws_access_key_id:
        os.environ["AWS_ACCESS_KEY_ID"]     = args.aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = args.aws_secret_access_key
        os.environ["AWS_DEFAULT_REGION"]    = args.aws_region
    _configure_s3(spark)
    s3_paths = {
        "customer": f"s3://{args.s3_bucket}/raw/customer/",
        "order":    f"s3://{args.s3_bucket}/raw/order/",
        "product":  f"s3://{args.s3_bucket}/raw/product/",
    }
    run_pipeline(
        spark, s3_paths,
        catalog=args.catalog,
        schema=args.schema,
        skip_dq_fail=args.skip_dq_fail,
        skip_catalog=args.skip_catalog,
    )
