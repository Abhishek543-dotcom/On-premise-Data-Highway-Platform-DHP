"""Batch Job 3: Filter high-value transactions."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job3-{args.tag}").getOrCreate()

    data = [(i, f"txn_{i:06d}", round(random.uniform(1, 5000), 2),
             random.choice(["US","UK","DE","JP","IN"]))
            for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("txn_ref", StringType()),
        StructField("amount", DoubleType()), StructField("country", StringType()),
    ])
    df = spark.createDataFrame(data, schema)
    high_value = df.filter(F.col("amount") > 1000)
    print(f"[Job3] High-value transactions: {high_value.count()} / {df.count()}")
    high_value.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job3_highvalue/")
    print("[Job3] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
