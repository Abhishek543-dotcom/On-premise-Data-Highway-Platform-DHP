"""Batch Job 9: Data partitioning by multiple keys."""
import argparse
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job9-{args.tag}").getOrCreate()

    countries = ["US", "UK", "DE", "JP", "IN", "BR"]
    years = ["2024", "2025", "2026"]
    data = [(i, random.choice(countries), random.choice(years),
             f"product_{random.randint(1,50)}", round(random.uniform(5, 500), 2))
            for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("country", StringType()),
        StructField("year", StringType()), StructField("product", StringType()),
        StructField("amount", DoubleType()),
    ])
    df = spark.createDataFrame(data, schema)
    print(f"[Job9] Writing {df.count()} records partitioned by country and year")
    df.write.mode("overwrite").partitionBy("country", "year") \
        .parquet("s3a://lakehouse-warehouse/batch10/job9_partitioned/")
    print("[Job9] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
