# Job Service

The central service for Spark job lifecycle management.

---

## Overview

- **Port**: 8001
- **Framework**: FastAPI + SQLAlchemy (async) + PostgreSQL + aiokafka
- **Container**: `lakehouse-job-service`

---

## API Endpoints

### Health

```
GET /health        → {"status": "healthy"}
GET /health/ready  → {"status": "ready"}
```

### Jobs

#### Submit Job

```bash
POST /api/v1/jobs/
```

```json
{
  "job_name": "daily_sales_etl",
  "job_type": "spark_etl",
  "entrypoint": "s3://lakehouse-scripts/etl/sales_transform.py",
  "arguments": ["--date", "2026-03-28", "--mode", "append"],
  "spark_config": {
    "spark.executor.memory": "2g",
    "spark.executor.cores": 2
  },
  "database_name": "sales_db",
  "table_name": "transactions",
  "submitted_by": "data_team",
  "max_retries": 3
}
```

Response (202):
```json
{
  "job_id": "uuid-here",
  "status": "QUEUED",
  "message": "Job accepted and queued for execution"
}
```

#### List Jobs

```bash
GET /api/v1/jobs/?page=1&page_size=20&status=RUNNING&job_type=spark_etl
```

#### Get Job

```bash
GET /api/v1/jobs/{job_id}
```

#### Cancel Job

```bash
DELETE /api/v1/jobs/{job_id}
```

#### Get Job Logs

```bash
GET /api/v1/jobs/{job_id}/logs?source=all&tail=500
```

---

## Job Types

| Type | Description |
|------|-------------|
| `spark_sql` | SQL-based Spark jobs |
| `spark_etl` | ETL transformation jobs |
| `spark_ml` | Machine learning jobs |
| `spark_streaming` | Streaming jobs |

---

## Authentication

- **External requests**: `X-API-Key` header
- **Internal callbacks**: `X-Internal-Token` header (Spark container → Job Service)

---

## Retry Logic

When a job reports `FAILED`:

1. Job Service checks `retry_count < max_retries`
2. If true: increment retry count, re-publish to Kafka
3. If false: mark job as `DEAD` (terminal state)

Terminal states: `SUCCESS`, `CANCELLED`, `DEAD`

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `KAFKA_BROKERS` | Yes | Kafka bootstrap servers |
| `REDIS_URL` | Yes | Redis connection URL |
| `LOG_SERVICE_URL` | Yes | Log Service internal URL |
| `API_KEY` | Yes | API key for authentication |
| `INTERNAL_API_TOKEN` | Yes | Token for internal callbacks |
| `AUTO_CREATE_TABLES` | No | Auto-create DB tables on startup |
