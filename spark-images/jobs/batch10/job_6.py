"""Batch Job 6: Deduplication and data quality checks."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job6-{args.tag}").getOrCreate()

    # Generate data with intentional duplicates
    base_data = [(i, f"email_{i % 300}@test.com", round(random.uniform(1, 100), 2))
                 for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("email", StringType()),
        StructField("score", DoubleType()),
    ])
    df = spark.createDataFrame(base_data, schema)

    total_before = df.count()
    deduped = df.dropDuplicates(["email"])
    total_after = deduped.count()
    print(f"[Job6] Before dedup: {total_before}, After dedup: {total_after}")
    print(f"[Job6] Duplicates removed: {total_before - total_after}")

    deduped.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job6_deduped/")
    print("[Job6] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
