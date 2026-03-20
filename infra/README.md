# infra/

Infrastructure-as-code placeholders for TDM Deckers.

## Structure

```
aws/
  main.tf          AWS provider + backend stub
  s3.tf            S3 buckets for staged TDM data (versioned, encrypted)
  iam.tf           IAM policy for Databricks → S3 access
databricks/
  workspace.tf     Databricks provider + Unity Catalog stubs
```

## AWS (Terraform)

```bash
cd infra/aws
terraform init
terraform plan -var="env=dev"
terraform apply -var="env=dev"
```

Credentials come from `~/.aws/credentials` (`aws configure`) — nothing is hardcoded.

## Databricks (Terraform)

```bash
cd infra/databricks
export DATABRICKS_HOST=https://...
export DATABRICKS_TOKEN=...
terraform init
terraform plan
```

## What to complete before applying

- `infra/aws/main.tf` — uncomment and configure the S3 remote state backend
- `infra/databricks/workspace.tf` — uncomment and configure Unity Catalog resources
- `infra/aws/iam.tf` — attach the policy to the Databricks IAM role ARN
