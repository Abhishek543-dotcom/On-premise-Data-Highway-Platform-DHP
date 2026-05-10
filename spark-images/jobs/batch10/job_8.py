"""Batch Job 8: Statistical distribution analysis."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job8-{args.tag}").getOrCreate()

    data = [(i, random.gauss(100, 25), random.choice(["A","B","C"]))
            for i in range(args.records)]
    schema = StructType([
        StructField("id", LongType()), StructField("measurement", DoubleType()),
        StructField("group", StringType()),
    ])
    df = spark.createDataFrame(data, schema)

    stats = df.groupBy("group").agg(
        F.count("*").alias("n"),
        F.round(F.mean("measurement"), 2).alias("mean"),
        F.round(F.stddev("measurement"), 2).alias("stddev"),
        F.round(F.min("measurement"), 2).alias("min"),
        F.round(F.max("measurement"), 2).alias("max"),
    )
    print("[Job8] Distribution statistics:")
    stats.show()
    stats.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job8_stats/")
    print("[Job8] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
