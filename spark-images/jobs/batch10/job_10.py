"""Batch Job 10: End-to-end pipeline (read, transform, validate, write)."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType, IntegerType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job10-{args.tag}").getOrCreate()

    # Stage 1: Generate raw data
    print("[Job10] Stage 1: Generating raw data")
    data = [(i, f"item_{random.randint(1,100)}", random.randint(1, 50),
             round(random.uniform(5, 200), 2), random.choice(["pending","shipped","delivered"]))
            for i in range(args.records)]
    schema = StructType([
        StructField("order_id", LongType()), StructField("item", StringType()),
        StructField("quantity", IntegerType()), StructField("unit_price", DoubleType()),
        StructField("status", StringType()),
    ])
    raw_df = spark.createDataFrame(data, schema)

    # Stage 2: Transform
    print("[Job10] Stage 2: Applying transformations")
    transformed = raw_df \
        .withColumn("total_price", F.round(F.col("quantity") * F.col("unit_price"), 2)) \
        .withColumn("is_high_value", F.col("quantity") * F.col("unit_price") > 1000) \
        .filter(F.col("status") != "pending")

    # Stage 3: Validate
    print("[Job10] Stage 3: Validation")
    null_count = transformed.filter(F.col("item").isNull()).count()
    negative_price = transformed.filter(F.col("total_price") < 0).count()
    print(f"[Job10] Null items: {null_count}, Negative prices: {negative_price}")
    assert null_count == 0, "Data quality check failed: null items found"
    assert negative_price == 0, "Data quality check failed: negative prices found"

    # Stage 4: Write
    print(f"[Job10] Stage 4: Writing {transformed.count()} validated records")
    transformed.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job10_pipeline/")

    print("[Job10] Pipeline complete")
    spark.stop()

if __name__ == "__main__":
    main()
