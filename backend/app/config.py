"""
Config-driven settings for the TDM backend.
All values read from environment variables or .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Databricks
    databricks_host:  str = ""
    databricks_token: str = ""

    # AWS
    aws_region:      str = "us-east-1"
    tdm_s3_bucket:   str = "tdm-deckers-staged-dev"

    # Unity Catalog / pipeline defaults
    tdm_catalog:        str = "tdm_catalog"
    tdm_schema_dev:     str = "tdm_dev"
    tdm_schema_staging: str = "tdm_staging"
    tdm_schema_prod:    str = "tdm_prod"

    # Databricks job IDs (set after workspace is configured)
    tdm_ingest_job_id:    str = ""
    tdm_pipeline_job_id:  str = ""


@lru_cache()
def get_settings() -> Settings:
    return Settings()
