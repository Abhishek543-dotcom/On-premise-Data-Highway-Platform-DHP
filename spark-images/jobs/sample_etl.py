"""
Sample ETL Job: Sales Transform
================================
Reads raw sales data from S3, applies transformations, and writes
to the lakehouse warehouse in Iceberg format.

Usage:
    spark-submit sample_etl.py --date 2026-03-28 --mode append
"""
import argparse
import sys
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Sales ETL Transform")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Processing date (YYYY-MM-DD)")
    parser.add_argument("--mode", default="append", choices=["append", "overwrite"],
                        help="Write mode")
    parser.add_argument("--records", type=int, default=1000,
                        help="Number of records to generate for demo")
    return parser.parse_args()


def create_sample_data(spark, num_records: int, process_date: str):
    """Generate sample sales data as a DataFrame."""
    import random

    data = []
    for i in range(num_records):
        data.append((
            i + 1,
            round(random.uniform(5.0, 500.0), 2),
            random.choice(["electronics", "clothing", "food", "home", "sports"]),
            random.choice(["US", "UK", "DE", "JP", "IN"]),
            process_date,
            f"customer_{random.randint(1, 200)}",
        ))

    schema = StructType([
        StructField("transaction_id", LongType(), False),
        StructField("amount", DoubleType(), False),
        StructField("category", StringType(), False),
        StructField("country", StringType(), False),
        StructField("txn_date", StringType(), False),
        StructField("customer_id", StringType(), False),
    ])

    return spark.createDataFrame(data, schema)


def transform(df):
    """Apply business transformations."""
    return (
        df
        .withColumn("amount_tax", F.round(F.col("amount") * 1.18, 2))
        .withColumn("amount_bucket",
                    F.when(F.col("amount") < 50, "low")
                     .when(F.col("amount") < 200, "medium")
                     .otherwise("high"))
        .withColumn("processed_at", F.current_timestamp())
    )


def main():
    args = parse_args()

    spark = SparkSession.builder \
        .appName(f"SalesETL-{args.date}") \
        .getOrCreate()

    print(f"[ETL] Processing date: {args.date}")
    print(f"[ETL] Mode: {args.mode}")
    print(f"[ETL] Generating {args.records} records")

    # Generate sample data
    raw_df = create_sample_data(spark, args.records, args.date)
    print(f"[ETL] Raw record count: {raw_df.count()}")

    # Transform
    transformed_df = transform(raw_df)
    print("[ETL] Transformation complete")
    transformed_df.show(5, truncate=False)

    # Write to warehouse
    output_path = "s3a://lakehouse-warehouse/sales_db/transactions/"
    print(f"[ETL] Writing to {output_path}")

    transformed_df.write \
        .mode(args.mode) \
        .partitionBy("txn_date") \
        .parquet(output_path)

    print(f"[ETL] Successfully wrote {transformed_df.count()} records")

    # Summary statistics
    summary = transformed_df.groupBy("category", "country").agg(
        F.count("*").alias("count"),
        F.round(F.sum("amount"), 2).alias("total_amount"),
        F.round(F.avg("amount"), 2).alias("avg_amount"),
    )
    print("[ETL] Summary:")
    summary.show(truncate=False)

    spark.stop()
    print("[ETL] Job completed successfully")


if __name__ == "__main__":
    main()
