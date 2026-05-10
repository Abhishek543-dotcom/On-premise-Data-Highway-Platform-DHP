# Spark Runtime Environment

How Spark jobs execute within the DataHarbour platform.

---

## Container Image

The Spark runtime image (`lakehouse-spark:3.5.0`) is built from `spark-images/base/Dockerfile`:

```
Base: apache/spark:3.5.0-python3
+ Apache Iceberg 1.5.0 runtime
+ AWS SDK Bundle 1.12.661
+ Hadoop AWS 3.3.4
+ curl, jq (for callbacks)
+ Custom entrypoint script
+ Fluent Bit config
```

Build it:

```bash
make build-spark
```

---

## Execution Model

Each job runs in its own **isolated Kubernetes pod** with `spark-submit --master local[*]`:

- No Spark cluster manager required
- Full CPU/memory isolation via K8s resource limits
- Pod is ephemeral - cleaned up after 1 hour (TTL)
- `backoff_limit=0` - no K8s-level retries (app-level only)

---

## Entrypoint Script

The container's entrypoint (`/opt/spark/entrypoint.sh`) does:

1. **Validates** required env vars (`JOB_ID`, `ENTRYPOINT_SCRIPT`)
2. **Resolves** `s3://` → `s3a://` for Hadoop compatibility
3. **Configures** Spark properties:
    - S3A filesystem (endpoint, credentials, path-style)
    - Iceberg catalog (`spark.sql.catalog.lakehouse`)
    - Hadoop catalog type with S3 warehouse
4. **Reports** `RUNNING` status via HTTP callback to Job Service
5. **Executes** `spark-submit --master local[*] <script>`
6. **Reports** terminal status (`SUCCESS`/`FAILED`) with exit code
7. **Waits** 5 seconds for log flush

---

## Pre-configured Spark Properties

| Property | Value |
|----------|-------|
| `spark.hadoop.fs.s3a.endpoint` | MinIO endpoint |
| `spark.hadoop.fs.s3a.path.style.access` | `true` |
| `spark.hadoop.fs.s3a.impl` | `org.apache.hadoop.fs.s3a.S3AFileSystem` |
| `spark.sql.catalog.lakehouse` | `org.apache.iceberg.spark.SparkCatalog` |
| `spark.sql.catalog.lakehouse.type` | `hadoop` |
| `spark.sql.catalog.lakehouse.warehouse` | `s3a://lakehouse-warehouse/` |

---

## Status Callback

The Spark container reports its lifecycle via HTTP:

```bash
PUT ${CALLBACK_URL}
Headers: X-Internal-Token: ${INTERNAL_API_TOKEN}
Body: {"status": "RUNNING|SUCCESS|FAILED", "exit_code": <int|null>}
```

The callback URL is injected as: `http://host.docker.internal:8001/api/v1/jobs/{job_id}/status`

---

## Log Shipping

When `ENABLE_FLUENT_BIT_SIDECAR=true`:

1. Spark writes to `/var/log/spark/${JOB_ID}.log`
2. Fluent Bit tails the log file
3. Adds labels: `job_id`, `container_id`, `source`
4. Ships to Loki at configured endpoint

---

## Resource Defaults

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 250m | 1000m |
| Memory | 512Mi | 2Gi |

Override via environment variables or per-job `spark_config`.
