# Databricks notebook source
# Exploratory notebook: inspect source domain tables in Unity Catalog

# COMMAND ----------
# MAGIC %md
# MAGIC ## TDM - Source Exploration
# MAGIC Use this notebook to inspect bronze/silver tables for a given domain.

# COMMAND ----------

catalog = "tdm_catalog"   # replace with your catalog
schema  = "tdm_dev"       # replace with your schema
domain  = "customer"      # change to: order, product, inventory, loyalty

# COMMAND ----------

df = spark.table(f"{catalog}.{schema}.bronze_{domain}")
print(f"Row count: {df.count()}")
df.printSchema()

# COMMAND ----------

display(df.limit(20))

# COMMAND ----------
# MAGIC %sql
# MAGIC DESCRIBE EXTENDED ${catalog}.${schema}.bronze_${domain}
