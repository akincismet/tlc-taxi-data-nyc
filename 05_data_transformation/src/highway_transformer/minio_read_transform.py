# 05_data_transformation/src/highway_transformer/minio_read_transform.py
"""
Load raw TLC Parquet partitions from MinIO (Bronze) and materialise **Silver**
fact- and dimension tables back to MinIO.

Run inside the Spark-on-K8s image:
    spark-submit minio_read_transform.py --run-date 2025-06-09
"""
import argparse, os
from pyspark.sql import SparkSession, functions as F, Window

load_dotenv()

# -----------------------------------------------------------------------------
# 1 — CLI & env
# -----------------------------------------------------------------------------
p = argparse.ArgumentParser()
p.add_argument("--run-date", help="YYYY-MM-DD (optional partition filter)")
args = p.parse_args()

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_ENDPOINT           = os.getenv("S3_ENDPOINT")           # http://minio:9000
BRONZE_BUCKET         = os.getenv("BRONZE_BUCKET", "bronze")
SILVER_BUCKET         = os.getenv("SILVER_BUCKET", "silver")
ZONE_LOOKUP_PATH      = os.getenv(
    "ZONE_LOOKUP_PATH",
    "s3a://bronze/lookup/taxi_zone_lookup.csv"
)

# -----------------------------------------------------------------------------
# 2 — Spark session (S3A → MinIO)
# -----------------------------------------------------------------------------
spark = (
    SparkSession.builder.appName("nyc-taxi-silver")
    .config("spark.hadoop.fs.s3a.access.key",    AWS_ACCESS_KEY_ID)
    .config("spark.hadoop.fs.s3a.secret.key",    AWS_SECRET_ACCESS_KEY)
    .config("spark.hadoop.fs.s3a.endpoint",      S3_ENDPOINT)
    .config("spark.hadoop.fs.s3a.path.style.access", True)
    .config("spark.sql.sources.partitionOverwriteMode", "dynamic")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

def bronze(pth: str) -> str: return f"s3a://{BRONZE_BUCKET}/{pth}"
def silver(pth: str) -> str: return f"s3a://{SILVER_BUCKET}/{pth}"

# -----------------------------------------------------------------------------
# 3 — Read raw trips
# -----------------------------------------------------------------------------
raw = (
    spark.read
    .parquet(bronze("yellow_tripdata_partitioned_by_day/*/*/*/*.parquet"))
    .withColumnRenamed("tpep_pickup_datetime",  "pickup_ts")
    .withColumnRenamed("tpep_dropoff_datetime", "dropoff_ts")
)

if args.run_date:
    raw = raw.filter(F.to_date("pickup_ts") == args.run_date)

# -----------------------------------------------------------------------------
# 4 — Dimensions
# -----------------------------------------------------------------------------
# 4.1 DimTime ---------------------------------------------------------------
def _dim_time(df, col):
    w = Window.orderBy(col)
    return (
        df.select(F.col(col).alias("ts")).distinct()
        .withColumn("Date",        F.to_date("ts"))
        .withColumn("DayOfMonth",  F.dayofmonth("ts"))
        .withColumn("WeekOfYear",  F.weekofyear("ts"))
        .withColumn("Month",       F.month("ts"))
        .withColumn("Year",        F.year("ts"))
        .withColumn("Hour",        F.hour("ts"))
        .withColumn("Minute",      F.minute("ts"))
        .withColumn("Second",      F.second("ts"))
        .withColumn("TimeID",      F.row_number().over(w))
    )

dim_time = (
    _dim_time(raw, "pickup_ts").unionByName(_dim_time(raw, "dropoff_ts"))
    .dropDuplicates(["TimeID"])
)

dim_time.write.mode("overwrite").partitionBy("Year", "Month")\
        .parquet(silver("dim_time"))

# 4.2 DimLocation -----------------------------------------------------------
lookup = (
    spark.read.option("header", True).csv(ZONE_LOOKUP_PATH)
              .withColumnRenamed("LocationID", "ZoneID")
)
dim_location = (
    lookup.withColumn("LocationID", F.col("ZoneID").cast("int"))
          .select("LocationID", "Borough", "Zone", "ServiceZone")
)
dim_location.write.mode("overwrite").parquet(silver("dim_location"))

# 4.3 DimRateCode & DimPayment ---------------------------------------------
rate_map = {1:"Standard rate",2:"JFK",3:"Newark",4:"Nassau or Westchester",5:"Negotiated fare",6:"Group ride"}
pay_map  = {1:"Credit card",2:"Cash",3:"No charge",4:"Dispute",5:"Unknown",6:"Voided trip"}

dim_rate = spark.createDataFrame([(k,v) for k,v in rate_map.items()],
                                 ["RateCodeID","RateDescription"])
dim_pay  = spark.createDataFrame([(k,v) for k,v in pay_map.items()],
                                 ["PaymentTypeID","PaymentType"])

dim_rate.write.mode("overwrite").parquet(silver("dim_rate_code"))
dim_pay.write.mode("overwrite").parquet(silver("dim_payment"))

# -----------------------------------------------------------------------------
# 5 — FactTrip
# -----------------------------------------------------------------------------
fact = (
    raw.alias("r")
    .join(dim_time.select("TimeID","ts").alias("pt"), F.col("r.pickup_ts")==F.col("pt.ts"),"left")
    .join(dim_time.select("TimeID","ts").alias("dt"), F.col("r.dropoff_ts")==F.col("dt.ts"),"left")
    .join(dim_location.alias("pl"), F.col("r.PULocationID")==F.col("pl.LocationID"),"left")
    .join(dim_location.alias("dl"), F.col("r.DOLocationID")==F.col("dl.LocationID"),"left")
    .join(dim_rate.alias("rc"), F.col("r.RatecodeID")==F.col("rc.RateCodeID"),"left")
    .join(dim_pay.alias("pp"),  F.col("r.payment_type")==F.col("pp.PaymentTypeID"),"left")
    .select(
        F.monotonically_increasing_id().alias("TripID"),
        F.col("pt.TimeID").alias("PickupDateTimeID"),
        F.col("dt.TimeID").alias("DropOffDateTimeID"),
        F.col("pl.LocationID").alias("PULocationID"),
        F.col("dl.LocationID").alias("DOLocationID"),
        "rc.RateCodeID",
        "pp.PaymentTypeID",
        F.col("passenger_count").cast("smallint").alias("PassengerCount"),
        F.col("trip_distance").cast("double").alias("TripDistance"),
        F.col("fare_amount").cast("decimal(10,2)").alias("FareAmount"),
        F.col("tip_amount").cast("decimal(10,2)").alias("TipAmount"),
        F.col("tolls_amount").cast("decimal(10,2)").alias("TollsAmount"),
        F.col("airport_fee").cast("decimal(10,2)").alias("AirportAmount"),
        F.col("total_amount").cast("decimal(10,2)").alias("TotalAmount"),
        F.col("extra").cast("decimal(10,2)").alias("Extra"),
        F.col("mta_tax").cast("decimal(10,2)").alias("MTATax"),
        F.col("congestion_surcharge").cast("decimal(10,2)").alias("CongestionSurcharge"),
        F.year("pickup_ts").alias("pickup_year"),
        F.month("pickup_ts").alias("pickup_month")
    )
)

fact.write.mode("overwrite").partitionBy("pickup_year","pickup_month")\
     .parquet(silver("fact_trip"))

spark.stop()
