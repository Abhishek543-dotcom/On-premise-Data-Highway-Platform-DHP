"""Batch Job 5: Join two datasets (orders + customers)."""
import argparse
import random
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType, IntegerType


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=1000)
    parser.add_argument("--tag", default="batch10")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"batch10-job5-{args.tag}").getOrCreate()

    # Customers dimension
    customers = [(i, f"customer_{i}", random.choice(["gold","silver","bronze"]),
                  random.choice(["US","UK","DE","JP"]))
                 for i in range(1, 201)]
    cust_schema = StructType([
        StructField("customer_id", IntegerType()), StructField("name", StringType()),
        StructField("tier", StringType()), StructField("country", StringType()),
    ])
    cust_df = spark.createDataFrame(customers, cust_schema)

    # Orders fact
    orders = [(i, random.randint(1, 200), round(random.uniform(10, 2000), 2))
              for i in range(args.records)]
    order_schema = StructType([
        StructField("order_id", LongType()), StructField("customer_id", IntegerType()),
        StructField("total", DoubleType()),
    ])
    order_df = spark.createDataFrame(orders, order_schema)

    joined = order_df.join(cust_df, "customer_id", "inner")
    summary = joined.groupBy("tier", "country").agg(
        F.count("*").alias("orders"), F.round(F.sum("total"), 2).alias("revenue"))
    print("[Job5] Customer-order join summary:")
    summary.show()
    joined.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/batch10/job5_joined/")
    print("[Job5] Complete")
    spark.stop()

if __name__ == "__main__":
    main()
