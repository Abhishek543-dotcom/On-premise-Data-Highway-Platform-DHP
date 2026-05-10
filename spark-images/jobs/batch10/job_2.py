"""Batch Job 2: Aggregate metrics by category."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job2-{args.tag}").getOrCreate()

    categories = ["electronics", "clothing", "food", "home", "sports", "books"]
    data = [(i, random.choice(categories), round(random.uniform(10, 1000), 2))
            for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("category", StringType()),
        StructField("revenue", DoubleType()),
    ])
    df = spark.createDataFrame(data, schema)
    agg = df.groupBy("category").agg(
        F.count("*").alias("count"), F.sum("revenue").alias("total_revenue"),
        F.avg("revenue").alias("avg_revenue"),
    )
    print("[Job2] Category aggregation:")
    agg.show()
    agg.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job2_agg/")
    print("[Job2] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
