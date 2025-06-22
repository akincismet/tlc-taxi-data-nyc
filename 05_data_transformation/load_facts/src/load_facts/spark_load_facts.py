import os
import pandas as pd
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *
import logging

DATA_DIR = "s3a://bronze/yellow_tripdata_partitioned_by_day/downloaded_yellow_tripdata/year=2024/month=1"

# Ensure the log directory exists
# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

def get_spark_session(app_name: str = "Load Facts") -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def create_nessie_database(spark: SparkSession, name: str = "silver"):
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS nessie.{name}")


# Write dimlocation
def write_fact_trip(spark: SparkSession, path: str = DATA_DIR, table_name: str = "fact_trip"):
    # Read txi zones
    df = spark.read.parquet(path)
    df2 = df.withColumn("PickupDateTimeID", F.date_format("tpep_pickup_datetime", "yyyyMMddHHmm").cast("long")) \
        .withColumn("DropOffDateTimeID", F.date_format("tpep_dropoff_datetime", "yyyyMMddHHmm").cast("long"))

    df3 = df2.select(
        F.monotonically_increasing_id().alias("TripID"),
        F.col("PickupDateTimeID"),
        F.col("DropOffDateTimeID"),
        F.col("PULocationID"),
        F.col("DOLocationID"),
        F.col("RatecodeID").alias("RateCodeID"),
        F.col("payment_type").alias("PaymentTypeID"),
        F.col("passenger_count").alias("PassengerCount"),
        F.col("trip_distance").alias("TripDistance"),
        F.col("fare_amount").alias("FareAmount"),
        F.col("tip_amount").alias("TipAmount"),
        F.col("tolls_amount").alias("TollsAmount"),
        F.col("Airport_fee").alias("AirportAmount"),
        F.col("total_amount").alias("TotalAmount"),
        F.col("extra").alias("Extra"),
        F.col("mta_tax").alias("MTATax"),
        F.col("congestion_surcharge").alias("CongestionSurcharge")
    )

    spark.sql(f"DROP TABLE IF EXISTS nessie.silver.{table_name}")

    spark.createDataFrame([], df3.schema).writeTo(f"nessie.silver.{table_name}").create()

    df3.write.format("iceberg").mode("overwrite") \
        .save(f"nessie.silver.{table_name}")


if __name__ == '__main__':
    spark = get_spark_session("Load Dimensions")

    create_nessie_database(spark, name="silver")

    write_fact_trip(spark, path=DATA_DIR, table_name='fact_trip')
