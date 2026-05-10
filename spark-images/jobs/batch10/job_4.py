"""Batch Job 4: Time-series data generation with windowing."""
import argparse
import random
from datetime import datetime, timedelta
from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job4-{args.tag}").getOrCreate()

    base_date = datetime(2026, 1, 1)
    sensors = [f"sensor_{i}" for i in range(1, 11)]
    data = [(i, random.choice(sensors), (base_date + timedelta(hours=i)).isoformat(),
             round(random.uniform(15, 45), 2))
            for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("sensor_id", StringType()),
        StructField("timestamp", StringType()), StructField("temperature", DoubleType()),
    ])
    df = spark.createDataFrame(data, schema)
    window = Window.partitionBy("sensor_id").orderBy("timestamp").rowsBetween(-2, 0)
    result = df.withColumn("moving_avg", F.round(F.avg("temperature").over(window), 2))
    print("[Job4] Moving average computed")
    result.show(10)
    result.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job4_timeseries/")
    print("[Job4] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
