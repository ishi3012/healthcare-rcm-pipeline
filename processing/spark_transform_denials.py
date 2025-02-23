"""
PySpark ETL for EDI 835 Denials Data

Goal:
- Reads staged denials data from JSON (produced by Kafka consumer).
- Cleans and transforms the data (error checking, type casting).
- Fix: Explicitly defines schema to ensure `billed_amount` is read correctly.
- Stores processed denials data in PostgreSQL for analytics.

"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder.appName("DenialsProcessing").getOrCreate()

# Define schema explicitly
schema = StructType([
    StructField("claim_id", StringType(), True),
    StructField("billed_amount", FloatType(), True),
    StructField("paid_amount", FloatType(), True),
    StructField("denial_reason", StringType(), True),
    StructField("status", StringType(), True)
])

# Read denials data from staging file with defined schema
df = spark.read.schema(schema).json("data_samples/staging_denials.json")

# Data Cleaning & Transformation
df_transformed = df.withColumn("billed_amount", col("billed_amount").cast("float"))

# # Show transformed data
# df_transformed.show()

# Save to PostgreSQL
df_transformed.write.format("jdbc").options(
    url="jdbc:postgresql://localhost:5432/rcm_db",
    driver="org.postgresql.Driver",
    dbtable="denials",
    user="admin",
    password="password"
).mode("append").save()

print("Denials data processed & stored in PostgreSQL")
