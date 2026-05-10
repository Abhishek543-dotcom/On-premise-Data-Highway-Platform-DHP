# Data Flow

Understanding how data flows through the DataHarbour platform.

---

## Job Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PENDING: POST /api/v1/jobs/
    PENDING --> QUEUED: Kafka publish success
    PENDING --> PENDING: Kafka publish failed (retry)
    QUEUED --> PROVISIONING: Orchestrator picks up event
    PROVISIONING --> RUNNING: Spark container reports
    RUNNING --> SUCCESS: Exit code 0
    RUNNING --> FAILED: Exit code != 0
    FAILED --> QUEUED: retry_count < max_retries
    FAILED --> DEAD: retry_count >= max_retries
    QUEUED --> CANCELLED: DELETE /api/v1/jobs/{id}
    PROVISIONING --> CANCELLED: DELETE /api/v1/jobs/{id}
    RUNNING --> CANCELLED: DELETE /api/v1/jobs/{id}
    
    SUCCESS --> [*]
    CANCELLED --> [*]
    DEAD --> [*]
```

---

## Detailed Event Flow

### 1. Job Submission

```mermaid
sequenceDiagram
    participant Client
    participant JS as Job Service
    participant PG as PostgreSQL
    participant K as Kafka
    
    Client->>JS: POST /api/v1/jobs/
    JS->>PG: INSERT job (status=PENDING)
    JS->>K: Publish to spark-job-submissions
    K-->>JS: ACK
    JS->>PG: UPDATE status=QUEUED
    JS-->>Client: 202 Accepted {job_id, status: QUEUED}
```

### 2. Orchestration

```mermaid
sequenceDiagram
    participant K as Kafka
    participant ORC as Orchestrator
    participant JS as Job Service
    participant K8S as Kubernetes
    
    K->>ORC: Consume job event
    ORC->>JS: PUT /status {PROVISIONING}
    ORC->>K8S: Create Job (spark-job-<id>-r<n>)
    K8S-->>ORC: Job created
    ORC->>JS: PUT /status {PROVISIONING, container_id}
```

### 3. Spark Execution

```mermaid
sequenceDiagram
    participant K8S as Kubernetes
    participant SPARK as Spark Container
    participant JS as Job Service
    participant MINIO as MinIO
    participant LOKI as Loki
    
    K8S->>SPARK: Start container
    SPARK->>JS: PUT /status {RUNNING}
    SPARK->>MINIO: Read input data (s3a://)
    SPARK->>SPARK: Execute spark-submit
    SPARK->>MINIO: Write output data (s3a://)
    SPARK->>JS: PUT /status {SUCCESS/FAILED}
    SPARK->>LOKI: Ship logs (via Fluent Bit)
```

### 4. Retry on Failure

```mermaid
sequenceDiagram
    participant SPARK as Spark Container
    participant JS as Job Service
    participant K as Kafka
    participant ORC as Orchestrator
    
    SPARK->>JS: PUT /status {FAILED, exit_code: 1}
    JS->>JS: Check: retry_count < max_retries?
    alt Has retries remaining
        JS->>JS: Increment retry_count
        JS->>K: Re-publish to spark-job-submissions
        K->>ORC: New attempt
    else Retries exhausted
        JS->>JS: Mark status = DEAD
    end
```

---

## Data Storage Layout

```
MinIO Buckets:
├── lakehouse-warehouse/     # Spark job outputs (Iceberg/Parquet)
│   ├── sales_db/
│   │   └── transactions/
│   └── batch10/
│       ├── job1_events/
│       └── ...
├── lakehouse-raw/           # Raw ingestion landing zone
├── lakehouse-scripts/       # Spark job Python scripts
│   ├── etl/
│   │   └── sales_transform.py
│   └── batch10/
│       ├── job_1.py
│       └── ...
└── lakehouse-logs/          # Archived logs
```

---

## Database Schema

### Jobs Tables

```sql
-- Core job tracking
jobs (
    job_id UUID PRIMARY KEY,
    job_name VARCHAR,
    job_type VARCHAR,      -- spark_sql, spark_etl, spark_ml, spark_streaming
    status VARCHAR,        -- PENDING, QUEUED, PROVISIONING, RUNNING, SUCCESS, FAILED, CANCELLED, DEAD
    entrypoint TEXT,
    arguments JSONB,
    spark_config JSONB,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    ...
)

-- Log references
job_log_refs (job_id, log_source, log_query)
```

### Catalog Tables

```sql
-- Database namespaces
catalog_databases (db_name, owner, description, ...)

-- Table metadata
catalog_tables (db_name, table_name, table_type, location, schema_json, ...)

-- Schema history
schema_history (table_id, version, operation, changes_json, ...)

-- Iceberg snapshots
table_snapshots (table_id, snapshot_id, operation, summary_json, ...)
```
