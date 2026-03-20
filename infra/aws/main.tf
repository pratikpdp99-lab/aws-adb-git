terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Stub: configure remote state when ready
  # backend "s3" {
  #   bucket = "tdm-terraform-state"
  #   key    = "infra/aws/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = "us-east-1"
  # Uses ~/.aws/credentials (aws configure) — no secrets in code
}
