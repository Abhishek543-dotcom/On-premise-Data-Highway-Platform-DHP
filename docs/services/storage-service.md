# Storage Service

S3/MinIO bucket and object management with presigned URL generation.

---

## Overview

- **Port**: 8004
- **Framework**: FastAPI + boto3
- **Container**: `lakehouse-storage-service`

---

## API Endpoints

### Create Bucket

```bash
POST /api/v1/storage/buckets
```

```json
{"name": "my-data-bucket"}
```

!!! note "Bucket Naming"
    Names must be 3-63 characters, lowercase, and match pattern `^[a-z0-9][a-z0-9.-]*[a-z0-9]$`

### List Buckets

```bash
GET /api/v1/storage/buckets
```

### List Objects

```bash
GET /api/v1/storage/buckets/{bucket_name}/objects?prefix=data/&max_keys=100
```

### Generate Presigned URL

```bash
POST /api/v1/storage/buckets/{bucket_name}/presigned-url
```

```json
{
  "object_key": "data/sales/2026/transactions.parquet",
  "operation": "download",
  "expiry": 3600
}
```

**Response:**

```json
{
  "bucket": "lakehouse-warehouse",
  "object_key": "data/sales/2026/transactions.parquet",
  "operation": "download",
  "url": "http://localhost:9000/lakehouse-warehouse/data/...?X-Amz-Signature=...",
  "expiry": 3600
}
```

### Delete Object

```bash
DELETE /api/v1/storage/buckets/{bucket_name}/objects/{object_key}
```

---

## Default Buckets

Created automatically on startup:

| Bucket | Purpose |
|--------|---------|
| `lakehouse-warehouse` | Spark job outputs (Iceberg/Parquet) |
| `lakehouse-raw` | Raw data landing zone |
| `lakehouse-scripts` | Spark job Python scripts |
| `lakehouse-logs` | Archived logs |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `S3_ENDPOINT` | Yes | MinIO/S3 endpoint |
| `S3_ACCESS_KEY` | Yes | Access key |
| `S3_SECRET_KEY` | Yes | Secret key |
| `S3_REGION` | No | S3 region (default: `us-east-1`) |
| `API_KEY` | Yes | API key for authentication |
