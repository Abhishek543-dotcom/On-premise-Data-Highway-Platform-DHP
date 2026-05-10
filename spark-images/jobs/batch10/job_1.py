"""Batch Job 1: Generate random user events and write to warehouse."""
import argparse
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job1-{args.tag}").getOrCreate()

    data = [(i, f"user_{random.randint(1,500)}", random.choice(["click","view","purchase","search"]),
             round(random.uniform(0, 100), 2)) for i in range(args.records)]
    schema = StructType([
        StructField("event_id", LongType()), StructField("user_id", StringType()),
        StructField("event_type", StringType()), StructField("value", DoubleType()),
    ])
    df = spark.createDataFrame(data, schema)
    print(f"[Job1] Generated {df.count()} user events")
    df.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job1_events/")
    print("[Job1] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
