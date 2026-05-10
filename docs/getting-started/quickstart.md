# Quick Start

Get the DataHarbour platform running locally in under 5 minutes.

---

## 1. Clone and Configure

```bash
git clone https://github.com/abhishektiwari/On-premise-Data-Highway-Platform-DHP.git
cd On-premise-Data-Highway-Platform-DHP

# Create your environment file from the template
cp .env.example .env
```

---

## 2. Verify Kubernetes

```bash
kubectl cluster-info
```

You should see your cluster's control plane address. If not, see [Prerequisites](prerequisites.md#kubernetes-cluster).

---

## 3. Build Spark Image

```bash
make build-spark
```

This builds the `lakehouse-spark:3.5.0` image with Iceberg and S3 support. Only needed once (or after changes to `spark-images/base/`).

---

## 4. Start the Platform

```bash
make up
```

This starts all 13 services via Docker Compose. Wait for all containers to be healthy:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

All containers should show `(healthy)` status within 30-60 seconds.

---

## 5. Verify Health

```bash
# API services
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:8002/health | jq .
curl -s http://localhost:8003/health | jq .
curl -s http://localhost:8004/health | jq .

# Infrastructure
curl -s http://localhost:3100/ready
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:9000/minio/health/live
```

---

## 6. Seed Sample Data

Upload sample Spark scripts to MinIO:

```bash
make seed
```

---

## 7. Submit Your First Job

```bash
curl -s -X POST http://localhost:8001/api/v1/jobs/ \
  -H "X-API-Key: dev-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "my_first_job",
    "job_type": "spark_etl",
    "entrypoint": "s3://lakehouse-scripts/etl/sample_etl.py",
    "arguments": ["--date", "2026-01-01", "--records", "500"],
    "spark_config": {
      "spark.executor.memory": "1g"
    },
    "submitted_by": "quickstart",
    "max_retries": 1
  }' | jq .
```

Save the returned `job_id` and check its status:

```bash
JOB_ID="<paste-job-id-here>"
curl -s -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8001/api/v1/jobs/${JOB_ID}" | jq '{job_id, status, retry_count}'
```

---

## 8. Explore the Platform

| URL | Description |
|-----|-------------|
| http://localhost:8001/docs | Job Service - Swagger UI |
| http://localhost:8002/docs | Metadata Service - Swagger UI |
| http://localhost:8003/docs | Log Service - Swagger UI |
| http://localhost:8004/docs | Storage Service - Swagger UI |
| http://localhost:3000 | Grafana (admin/admin) |
| http://localhost:9001 | MinIO Console |
| http://localhost:9090 | Prometheus |

---

## 9. Stop the Platform

```bash
make down
```

To completely reset (removes volumes):

```bash
make clean
```

---

## Next Steps

- [Architecture Overview](../architecture/overview.md) - Understand the system design
- [Writing Spark Jobs](../spark/writing-jobs.md) - Create custom Spark jobs
- [Configuration Reference](configuration.md) - Customize environment variables
- [Operations Runbook](../operations/runbook.md) - Production-style operations
