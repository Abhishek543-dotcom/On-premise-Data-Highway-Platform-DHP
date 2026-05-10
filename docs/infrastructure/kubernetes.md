# Kubernetes

Kubernetes manifests for production-style deployment.

---

## Overview

The `infra/k8s/` directory contains raw Kubernetes YAML manifests (no Helm).

---

## Namespaces

| Namespace | Purpose |
|-----------|---------|
| `lakehouse-platform` | Application services |
| `lakehouse-jobs` | Spark job execution (isolated) |

---

## Manifests

| File | Resources |
|------|-----------|
| `namespaces.yaml` | Namespace definitions |
| `config.yaml` | ConfigMap + Secret (shared config) |
| `fluent-bit-config.yaml` | Fluent Bit sidecar configuration |
| `network-policy.yaml` | Spark pod network restrictions |
| `orchestrator-deployment.yaml` | Orchestrator Deployment + RBAC |
| `job-service-deployment.yaml` | Job Service Deployment + Service |
| `metadata-service-deployment.yaml` | Metadata Service Deployment + Service |
| `log-service-deployment.yaml` | Log Service Deployment + Service |
| `storage-service-deployment.yaml` | Storage Service Deployment + Service |

---

## Deployment

```bash
# Apply all manifests
make k8s-deploy

# Remove all manifests
make k8s-delete
```

---

## RBAC

The Orchestrator has a dedicated ServiceAccount with Role/RoleBinding:

```yaml
rules:
  - apiGroups: ["batch"]
    resources: ["jobs"]
    verbs: ["create", "delete", "get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
```

A `spark-runner` ServiceAccount is created in `lakehouse-jobs` for Spark pods.

---

## Network Policy

Spark pods are isolated with egress-only rules:

```yaml
# Allowed egress from Spark pods:
- MinIO: port 9000 (in lakehouse-platform)
- Kafka: port 9092 (in lakehouse-platform)  
- Job Service: port 8000 (in lakehouse-platform)
- DNS: port 53 (any)

# No ingress allowed (Spark pods receive no incoming traffic)
```

---

## Service Replicas

| Service | Replicas | Probes |
|---------|----------|--------|
| Job Service | 3 | Liveness + Readiness on `/health` |
| Metadata Service | 2 | Liveness + Readiness on `/health` |
| Log Service | 2 | Liveness + Readiness on `/health` |
| Storage Service | 2 | Liveness + Readiness on `/health` |
| Orchestrator | 2 | -- (event-driven) |

---

## ConfigMap Values

```yaml
KAFKA_BROKERS: kafka.lakehouse-platform.svc:9092
REDIS_URL: redis://redis.lakehouse-platform.svc:6379
S3_ENDPOINT: http://minio.lakehouse-platform.svc:9000
LOKI_URL: http://loki.lakehouse-platform.svc:3100
DATABASE_URL: postgresql+asyncpg://lakehouse:<pw>@postgres.lakehouse-platform.svc:5432/lakehouse
```
