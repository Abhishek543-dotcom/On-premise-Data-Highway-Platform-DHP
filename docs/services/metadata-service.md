# Metadata Service

Manages the lakehouse catalog: databases, tables, schema evolution, and snapshots.

---

## Overview

- **Port**: 8002
- **Framework**: FastAPI + SQLAlchemy (async) + PostgreSQL
- **Container**: `lakehouse-metadata-service`

---

## API Endpoints

### Databases

#### Create Database

```bash
POST /api/v1/databases/
```

```json
{
  "db_name": "sales_db",
  "owner": "data_team",
  "description": "Sales domain data"
}
```

#### List Databases

```bash
GET /api/v1/databases/
```

#### Get Database

```bash
GET /api/v1/databases/{db_name}
```

#### Delete Database

```bash
DELETE /api/v1/databases/{db_name}
```

### Tables

#### Create Table

```bash
POST /api/v1/databases/{db_name}/tables/
```

```json
{
  "table_name": "transactions",
  "table_type": "ICEBERG",
  "schema_fields": [
    {"name": "id", "type": "long", "nullable": false},
    {"name": "amount", "type": "double", "nullable": false},
    {"name": "txn_date", "type": "string", "nullable": false}
  ],
  "partition_spec": [
    {"field": "txn_date", "transform": "day"}
  ]
}
```

#### Update Table (Schema Evolution)

```bash
PUT /api/v1/databases/{db_name}/tables/{table_name}
```

```json
{
  "add_columns": [
    {"name": "region", "type": "string", "nullable": true}
  ],
  "drop_columns": ["deprecated_field"],
  "rename_columns": {"old_name": "new_name"}
}
```

#### List Snapshots

```bash
GET /api/v1/databases/{db_name}/tables/{table_name}/snapshots
```

---

## Table Types

| Type | Description |
|------|-------------|
| `ICEBERG` | Apache Iceberg format (recommended) |
| `DELTA` | Delta Lake format |
| `HIVE` | Hive table format |
| `PARQUET` | Plain Parquet files |

---

## Schema Evolution

The service tracks all schema changes in `schema_history`:

- **Add columns** - New nullable columns appended
- **Drop columns** - Soft delete with history preserved
- **Rename columns** - Tracked with old/new names

Each change increments the schema version.

---

## Table Location

Tables are automatically located at:

```
s3://lakehouse-warehouse/{db_name}/{table_name}/
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `S3_ENDPOINT` | Yes | MinIO/S3 endpoint |
| `S3_ACCESS_KEY` | Yes | S3 access key |
| `S3_SECRET_KEY` | Yes | S3 secret key |
| `S3_WAREHOUSE_BUCKET` | Yes | Default warehouse bucket |
| `API_KEY` | Yes | API key for authentication |
