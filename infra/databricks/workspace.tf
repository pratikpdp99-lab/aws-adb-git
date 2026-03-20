terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

provider "databricks" {
  # Uses DATABRICKS_HOST + DATABRICKS_TOKEN env vars — no secrets in code
}

# Placeholder: Unity Catalog setup
# resource "databricks_catalog" "tdm" {
#   name    = "tdm_catalog"
#   comment = "TDM platform catalog"
# }

# Placeholder: cluster policy
# resource "databricks_cluster_policy" "tdm" {
#   name = "tdm-cluster-policy"
#   definition = jsonencode({...})
# }
