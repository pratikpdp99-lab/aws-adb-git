# Placeholder: S3 buckets for TDM staged data
# Replace <your-account-id> and <env> with real values before applying.

variable "env" {
  default = "dev"
}

resource "aws_s3_bucket" "tdm_staged" {
  bucket = "tdm-deckers-staged-${var.env}"

  tags = {
    Project     = "tdm-deckers"
    Environment = var.env
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "tdm_staged" {
  bucket = aws_s3_bucket.tdm_staged.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tdm_staged" {
  bucket = aws_s3_bucket.tdm_staged.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
