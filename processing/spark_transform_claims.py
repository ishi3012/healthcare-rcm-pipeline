"""
  PySpark ETL for EDI 837 Claims Data.

  - Reads staged claims from JSON (produced by Kafka consumer).
  - Cleans and transforms the data.
  - Stores transformed data in PstgreSQL for analytics. 

"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder.appName("ClaimsProcessing").getOrCreate()

# Read claims data from staging file
df = spark.read.json("data_samples/staging_claims.json")

# Data Cleaning and Transformation
df_transformed = df.withColumn("billed_amount", col("billed_amount").cast("float"))

# # Show transformed data
# df_transformed.show()

# Save to PostgreSQL
df_transformed.write.format("jdbc").options(
    url = "jdbc:postgresql://localhost:5432/rcm_db",
    driver="org.postgresql.Driver",
    dbtable="claims",
    user="admin",
    password="password"
).mode("append").save()

print(f"Claims data processed & stored in PostgreSQL")