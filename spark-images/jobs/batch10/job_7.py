"""Batch Job 7: Pivot table generation."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job7-{args.tag}").getOrCreate()

    regions = ["north", "south", "east", "west"]
    products = ["widget_a", "widget_b", "widget_c", "widget_d"]
    months = ["2026-01", "2026-02", "2026-03"]

    data = [(i, random.choice(regions), random.choice(products),
             random.choice(months), round(random.uniform(100, 10000), 2))
            for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("region", StringType()),
        StructField("product", StringType()), StructField("month", StringType()),
        StructField("sales", DoubleType()),
    ])
    df = spark.createDataFrame(data, schema)
    pivot = df.groupBy("region").pivot("month").agg(F.round(F.sum("sales"), 2))
    print("[Job7] Pivot table:")
    pivot.show()
    pivot.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job7_pivot/")
    print("[Job7] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
