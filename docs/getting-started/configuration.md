# Configuration

All configuration is driven by environment variables. Copy `.env.example` to `.env` and adjust as needed.

---

## Environment Variables Reference

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_PASSWORD` | `dev-db-password-change-me` | PostgreSQL password |

The database URL is constructed in docker-compose as:  
`postgresql+asyncpg://lakehouse:<password>@postgres:5432/lakehouse`

---

### Object Storage (MinIO/S3)

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_ACCESS_KEY` | `dev-access-key-change-me` | MinIO/S3 access key |
| `S3_SECRET_KEY` | `dev-secret-key-change-me` | MinIO/S3 secret key |

---

### API Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `dev-api-key-change-me` | API key for external requests (`X-API-Key` header) |
| `INTERNAL_API_TOKEN` | `dev-internal-token-change-me` | Token for internal callbacks (`X-Internal-Token` header) |

---

### CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated allowed origins |

---

### Orchestrator - Kubernetes

| Variable | Default | Description |
|----------|---------|-------------|
| `K8S_HOST_ALIAS` | `host.docker.internal` | Hostname for K8s API access from Docker |
| `K8S_SKIP_TLS_VERIFY` | `true` | Skip TLS verification (local dev only) |
| `JOB_SERVICE_URL` | `http://job-service:8000` | Internal service URL (Docker network) |

---

### Orchestrator - Runtime Endpoints

These are what the Spark container sees from inside the Kubernetes cluster. They must resolve to the host machine where Docker services run.

| Variable | Default | Description |
|----------|---------|-------------|
| `RUNTIME_KAFKA_BROKERS` | `host.docker.internal:29092` | Kafka broker for Spark containers |
| `RUNTIME_JOB_SERVICE_URL` | `http://host.docker.internal:8001` | Job Service callback URL for Spark containers |
| `RUNTIME_S3_ENDPOINT` | `http://host.docker.internal:9000` | MinIO endpoint for Spark containers |

---

### Orchestrator - Spark Resource Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_CPU_REQUEST` | `250m` | CPU request per Spark pod |
| `DEFAULT_CPU_LIMIT` | `1000m` | CPU limit per Spark pod |
| `DEFAULT_MEMORY_REQUEST` | `512Mi` | Memory request per Spark pod |
| `DEFAULT_MEMORY_LIMIT` | `2Gi` | Memory limit per Spark pod |
| `ENABLE_FLUENT_BIT_SIDECAR` | `true` | Enable log shipping sidecar |

!!! warning "Resource Scheduling"
    If Spark pods are stuck in `Pending`, reduce these values. Local Kubernetes clusters often have limited resources.

---

### Per-Service Configuration

Each service also supports:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_CREATE_TABLES` | `true` | Auto-create database tables on startup |
| `DEBUG` | `false` | Enable debug logging |
| `CORS_ALLOWED_ORIGINS` | (see above) | CORS origins |

---

## Docker Compose Overrides

For local customization, create `infra/docker-compose.override.yaml`:

```yaml
services:
  job-service:
    environment:
      DEBUG: "true"
  orchestrator:
    environment:
      DEFAULT_CPU_REQUEST: "100m"
      DEFAULT_MEMORY_REQUEST: "256Mi"
```

This file is automatically merged with the main compose file.
