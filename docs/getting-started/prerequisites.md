# Prerequisites

Before running DataHarbour Project, ensure you have the following installed.

---

## Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | Latest | Container runtime with Compose |
| Python | 3.11+ | Service development and testing |
| kubectl | Latest | Kubernetes CLI for Spark execution |
| A local K8s cluster | -- | e.g., Docker Desktop K8s, minikube, kind |

---

## Verifying Your Setup

```bash
# Docker
docker --version
docker compose version

# Python
python3 --version

# Kubernetes
kubectl cluster-info
kubectl version --short
```

---

## Kubernetes Cluster

The platform requires a local Kubernetes cluster for Spark job execution. The simplest options:

### Option 1: Docker Desktop Kubernetes (Recommended)

1. Open Docker Desktop Settings
2. Go to **Kubernetes** tab
3. Check **Enable Kubernetes**
4. Click **Apply & Restart**
5. Wait for the green indicator

### Option 2: minikube

```bash
minikube start --cpus=4 --memory=8192
```

### Option 3: kind

```bash
kind create cluster --name lakehouse
```

---

## Kubeconfig

The orchestrator container mounts `~/.kube/config` to communicate with your local cluster. Verify it exists:

```bash
ls ~/.kube/config
```

---

## Resource Requirements

For local development with all services running:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB | 20 GB |

Spark jobs run as separate K8s pods with configurable resource limits (default: 250m-1000m CPU, 512Mi-2Gi memory).

---

## Network Ports

The following ports must be available:

| Port | Service |
|------|---------|
| 3000 | Grafana |
| 3100 | Loki |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8001-8004 | Application services |
| 9000-9001 | MinIO |
| 9090 | Prometheus |
| 9092, 29092 | Kafka |
| 9115 | Blackbox Exporter |
