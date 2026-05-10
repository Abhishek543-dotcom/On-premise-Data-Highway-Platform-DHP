# API Reference

Complete REST API documentation for all DataHarbour services.

---

## Authentication

All business endpoints require the `X-API-Key` header:

```bash
-H "X-API-Key: dev-api-key-change-me"
```

Internal status callback endpoint requires `X-Internal-Token`:

```bash
-H "X-Internal-Token: dev-internal-token-change-me"
```

Health endpoints (`/health`, `/health/ready`) are unauthenticated.

---

## Interactive API Docs

Each service provides Swagger UI:

| Service | URL |
|---------|-----|
| Job Service | http://localhost:8001/docs |
| Metadata Service | http://localhost:8002/docs |
| Log Service | http://localhost:8003/docs |
| Storage Service | http://localhost:8004/docs |

ReDoc is also available at `/redoc` on each service.

---

## OpenAPI Specification

The full OpenAPI 3.0 spec is available at: `docs/api-spec.yaml`

---

## Job Service (Port 8001)

### Submit Job
`POST /api/v1/jobs/` → 202

### List Jobs
`GET /api/v1/jobs/?page=1&page_size=20&status=RUNNING&job_type=spark_etl&submitted_by=user`

### Get Job
`GET /api/v1/jobs/{job_id}`

### Cancel Job
`DELETE /api/v1/jobs/{job_id}`

### Update Status (Internal)
`PUT /api/v1/jobs/{job_id}/status`

### Get Logs
`GET /api/v1/jobs/{job_id}/logs?source=all&tail=500`

---

## Metadata Service (Port 8002)

### Create Database
`POST /api/v1/databases/`

### List Databases
`GET /api/v1/databases/`

### Get Database
`GET /api/v1/databases/{db_name}`

### Delete Database
`DELETE /api/v1/databases/{db_name}`

### Create Table
`POST /api/v1/databases/{db_name}/tables/`

### List Tables
`GET /api/v1/databases/{db_name}/tables/`

### Get Table
`GET /api/v1/databases/{db_name}/tables/{table_name}`

### Update Table (Schema Evolution)
`PUT /api/v1/databases/{db_name}/tables/{table_name}`

### Delete Table
`DELETE /api/v1/databases/{db_name}/tables/{table_name}`

### List Snapshots
`GET /api/v1/databases/{db_name}/tables/{table_name}/snapshots`

---

## Log Service (Port 8003)

### Get Logs
`GET /api/v1/logs/{job_id}?source=all&tail=500`

### Stream Logs (SSE)
`GET /api/v1/logs/{job_id}/stream?source=all`

---

## Storage Service (Port 8004)

### Create Bucket
`POST /api/v1/storage/buckets` → 201

### List Buckets
`GET /api/v1/storage/buckets`

### List Objects
`GET /api/v1/storage/buckets/{bucket_name}/objects?prefix=&max_keys=1000`

### Presigned URL
`POST /api/v1/storage/buckets/{bucket_name}/presigned-url`

### Delete Object
`DELETE /api/v1/storage/buckets/{bucket_name}/objects/{object_key}` → 204

---

## Postman Collection

Pre-built Postman collection available in `docs/postman/`:

- `lakehouse-platform.postman_collection.json`
- `lakehouse-platform.local.postman_environment.json`

Import both into Postman and run folders in order:

1. Metadata Service
2. Storage Service
3. Job Service
4. Log Service
