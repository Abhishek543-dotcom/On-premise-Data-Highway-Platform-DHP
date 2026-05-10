# Operations Runbook

Procedures for operating the DataHarbour platform.

---

## Prerequisites

- Docker Desktop running
- Python 3.11+
- `kubectl` configured and healthy
- `~/.kube/config` available

Verify:
```bash
docker --version
kubectl cluster-info
```

---

## Start and Stop

### Start Stack

```bash
cp .env.example .env    # First time only
make build-spark        # First time only
make up
```

### Stop Stack

```bash
make down
```

### Full Cleanup (removes all data)

```bash
make clean
```

---

## Health Verification

### API Services

```bash
curl -s http://localhost:8001/health | jq .
curl -s http://localhost:8001/health/ready | jq .
curl -s http://localhost:8002/health | jq .
curl -s http://localhost:8003/health | jq .
curl -s http://localhost:8004/health | jq .
```

### Infrastructure

```bash
curl -s http://localhost:3100/ready
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:3000/api/health
curl -s http://localhost:9000/minio/health/live
```

### Metrics Endpoints

```bash
curl -s http://localhost:8001/metrics | head -5
curl -s http://localhost:8002/metrics | head -5
curl -s http://localhost:8003/metrics | head -5
curl -s http://localhost:8004/metrics | head -5
```

---

## Functional Smoke Test

### 1. Create Metadata

```bash
export API_KEY="dev-api-key-change-me"

# Create database
curl -s -X POST http://localhost:8002/api/v1/databases/ \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "db_name": "sales_db",
    "owner": "platform_ops",
    "description": "Sales domain"
  }' | jq .

# Create table
curl -s -X POST http://localhost:8002/api/v1/databases/sales_db/tables/ \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "transactions",
    "table_type": "ICEBERG",
    "schema_fields": [
      {"name": "id", "type": "long", "nullable": false},
      {"name": "amount", "type": "double", "nullable": false},
      {"name": "txn_date", "type": "string", "nullable": false}
    ],
    "partition_spec": [{"field": "txn_date", "transform": "day"}]
  }' | jq .
```

### 2. Verify Storage

```bash
curl -s -X POST http://localhost:8004/api/v1/storage/buckets \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name":"smoke-test-bucket"}' | jq .
```

### 3. Submit a Spark Job

```bash
curl -s -X POST http://localhost:8001/api/v1/jobs/ \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "smoke_test_etl",
    "job_type": "spark_etl",
    "entrypoint": "s3://lakehouse-scripts/etl/sample_etl.py",
    "arguments": ["--date", "2026-03-28", "--records", "500"],
    "spark_config": {"spark.executor.memory": "1g"},
    "database_name": "sales_db",
    "table_name": "transactions",
    "submitted_by": "runbook",
    "max_retries": 1
  }' | jq .
```

### 4. Monitor Job

```bash
JOB_ID="<paste-id-here>"
# Poll status
curl -s -H "X-API-Key: ${API_KEY}" \
  "http://localhost:8001/api/v1/jobs/${JOB_ID}" | jq '{job_id,status,retry_count}'
```

### 5. Fetch Logs

```bash
curl -s -H "X-API-Key: ${API_KEY}" \
  "http://localhost:8001/api/v1/jobs/${JOB_ID}/logs?tail=100" | jq '.entries[-5:]'
```

---

## Batch Execution

Submit 10 parallel jobs:

```bash
for i in $(seq 1 10); do
  curl -s -X POST http://localhost:8001/api/v1/jobs/ \
    -H "X-API-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
      \"job_name\": \"batch10_job_${i}\",
      \"job_type\": \"spark_etl\",
      \"entrypoint\": \"s3://lakehouse-scripts/batch10/job_${i}.py\",
      \"arguments\": [\"--records\", \"1200\", \"--tag\", \"batch10\"],
      \"spark_config\": {\"spark.executor.memory\": \"1g\"},
      \"submitted_by\": \"runbook_batch\",
      \"max_retries\": 1
    }" | jq -r '.job_id'
done
```

Track all jobs:
```bash
curl -s -H "X-API-Key: ${API_KEY}" \
  "http://localhost:8001/api/v1/jobs/?page_size=50" \
  | jq '.jobs[] | {job_id,job_name,status}'
```

---

## Kubernetes Operations

### Inspect Spark Jobs

```bash
kubectl get jobs -n lakehouse-jobs
kubectl get pods -n lakehouse-jobs
```

### Pod Logs

```bash
kubectl logs -n lakehouse-jobs <pod-name> -c spark-<jobid8>
kubectl logs -n lakehouse-jobs <pod-name> -c fluent-bit
```

### Pod Events

```bash
kubectl describe pod -n lakehouse-jobs <pod-name>
```

---

## Grafana Operations

- **Dashboard URL**: http://localhost:3000/d/lakehouse-admin-ops
- **Login**: admin / admin

### Prometheus Target Health

```bash
curl -s http://localhost:9090/api/v1/targets \
  | jq '{active:(.data.activeTargets|length), healthy:(.data.activeTargets|map(select(.health=="up"))|length)}'
```

---

## Database Management

```bash
# Initialize schema
make db-init

# Reset schema (destructive)
make db-reset
```

---

## Seed Data

Upload sample Spark scripts to MinIO:

```bash
make seed
```
