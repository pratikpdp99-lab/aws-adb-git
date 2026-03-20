# Placeholder: IAM policy allowing Databricks to read/write TDM S3 buckets.
# Attach this policy to the Databricks IAM role in your workspace.

resource "aws_iam_policy" "tdm_s3_access" {
  name        = "tdm-deckers-s3-access-${var.env}"
  description = "Allow Databricks to read/write TDM staged S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.tdm_staged.arn,
          "${aws_s3_bucket.tdm_staged.arn}/*"
        ]
      }
    ]
  })
}
