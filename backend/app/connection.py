"""
Connection utilities for TDM project.
Loads credentials from .env file (never commit .env to git).
"""

import os
import boto3
from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient

load_dotenv()


def get_databricks_client() -> WorkspaceClient:
    """Return an authenticated Databricks WorkspaceClient."""
    return WorkspaceClient(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
    )


def get_aws_session(region: str = None) -> boto3.Session:
    """Return a boto3 Session. Uses ~/.aws/credentials by default (aws configure).
    Override region via AWS_REGION in .env or pass region explicitly.
    """
    return boto3.Session(region_name=region or os.environ.get("AWS_REGION", "us-east-1"))


def get_s3_client():
    """Return an S3 client."""
    return get_aws_session().client("s3")


if __name__ == "__main__":
    # Test Databricks
    w = get_databricks_client()
    me = w.current_user.me()
    print(f"Databricks  : {me.user_name} @ {w.config.host}")

    # Test AWS
    sts = get_aws_session().client("sts")
    identity = sts.get_caller_identity()
    print(f"AWS         : {identity['Arn']}")
    print(f"AWS Account : {identity['Account']}")
