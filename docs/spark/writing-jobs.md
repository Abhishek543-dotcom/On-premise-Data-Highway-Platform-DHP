# Writing Spark Jobs

How to write, deploy, and submit PySpark jobs to the DataHarbour platform.

---

## Job Structure

A DHP Spark job is a standard PySpark script. The platform provides:

- Pre-configured `SparkSession` with S3/Iceberg settings
- Automatic `s3://` → `s3a://` path resolution
- Status callbacks handled by the entrypoint wrapper

Your script just needs to do its work and exit with code 0 (success) or non-zero (failure).

---

## Minimal Example

```python
from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("MyJob") \
        .getOrCreate()

    # Your logic here
    df = spark.read.parquet("s3a://lakehouse-warehouse/input/")
    result = df.filter(df.amount > 100)
    result.write.mode("overwrite").parquet("s3a://lakehouse-warehouse/output/")

    spark.stop()

if __name__ == "__main__":
    main()
```

---

## Using Arguments

```python
import argparse
from pyspark.sql import SparkSession

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--mode", default="append")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(f"ETL-{args.date}").getOrCreate()
    # Use args.date and args.mode in your logic
    spark.stop()

if __name__ == "__main__":
    main()
```

Submit with arguments:

```json
{
  "entrypoint": "s3://lakehouse-scripts/etl/my_job.py",
  "arguments": ["--date", "2026-03-28", "--mode", "append"]
}
```

---

## Using the Iceberg Catalog

The runtime pre-configures an Iceberg catalog named `lakehouse`:

```python
spark.sql("CREATE TABLE lakehouse.db.my_table (id BIGINT, name STRING)")
spark.sql("INSERT INTO lakehouse.db.my_table VALUES (1, 'hello')")
spark.sql("SELECT * FROM lakehouse.db.my_table").show()
```

---

## Deploying Jobs

### 1. Write your script

Save it under `spark-images/jobs/` for version control.

### 2. Upload to MinIO

```bash
# Using mc (MinIO Client)
mc cp spark-images/jobs/my_job.py lakehouse/lakehouse-scripts/etl/my_job.py

# Or via Storage Service API
curl -X POST http://localhost:8004/api/v1/storage/buckets/lakehouse-scripts/presigned-url \
  -H "X-API-Key: dev-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"object_key": "etl/my_job.py", "operation": "upload"}'
# Then upload using the returned presigned URL
```

### 3. Submit via API

```bash
curl -X POST http://localhost:8001/api/v1/jobs/ \
  -H "X-API-Key: dev-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "my_etl_job",
    "job_type": "spark_etl",
    "entrypoint": "s3://lakehouse-scripts/etl/my_job.py",
    "arguments": ["--date", "2026-03-28"],
    "spark_config": {},
    "submitted_by": "developer",
    "max_retries": 2
  }'
```

---

## Extra Spark Configuration

Pass custom Spark configuration per job:

```json
{
  "spark_config": {
    "spark.executor.memory": "4g",
    "spark.executor.cores": 2,
    "spark.sql.shuffle.partitions": 200,
    "spark.driver.maxResultSize": "2g"
  }
}
```

These are injected as `SPARK_EXTRA_CONF` and appended to spark-submit.

---

## Sample Jobs Included

| Job | Path | Description |
|-----|------|-------------|
| Sample ETL | `spark-images/jobs/sample_etl.py` | Sales data transform with partitioning |
| Random Data | `spark-images/jobs/job.py` | Simple data generation |
| Batch 1 | `spark-images/jobs/batch10/job_1.py` | User event generation |
| Batch 2 | `spark-images/jobs/batch10/job_2.py` | Category aggregation |
| Batch 3 | `spark-images/jobs/batch10/job_3.py` | High-value filtering |
| Batch 4 | `spark-images/jobs/batch10/job_4.py` | Time-series windowing |
| Batch 5 | `spark-images/jobs/batch10/job_5.py` | Join operations |
| Batch 6 | `spark-images/jobs/batch10/job_6.py` | Deduplication |
| Batch 7 | `spark-images/jobs/batch10/job_7.py` | Pivot tables |
| Batch 8 | `spark-images/jobs/batch10/job_8.py` | Statistical analysis |
| Batch 9 | `spark-images/jobs/batch10/job_9.py` | Multi-key partitioning |
| Batch 10 | `spark-images/jobs/batch10/job_10.py` | End-to-end pipeline |

---

## Monitoring Your Job

```bash
# Check status
curl -s -H "X-API-Key: dev-api-key-change-me" \
  http://localhost:8001/api/v1/jobs/${JOB_ID} | jq '{status, retry_count}'

# Check logs
curl -s -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8001/api/v1/jobs/${JOB_ID}/logs?tail=100" | jq '.entries[-5:]'

# Check K8s pod
kubectl get pods -n lakehouse-jobs -l job-id=${JOB_ID}
```
