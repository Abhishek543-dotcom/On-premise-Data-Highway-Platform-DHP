# Troubleshooting

Common issues and their solutions.

---

## Jobs Stuck in PENDING or QUEUED

**Symptoms**: Jobs submitted but never progress past QUEUED.

**Check**:
```bash
docker logs lakehouse-kafka --tail 100
docker logs lakehouse-orchestrator --tail 200
```

**Fixes**:
- Verify Kafka is healthy: `docker exec lakehouse-kafka kafka-topics --bootstrap-server localhost:9092 --list`
- Verify orchestrator is running and connected to Kafka
- Check if the orchestrator can reach the Job Service

---

## Orchestrator Cannot Reach Kubernetes

**Symptoms**: Jobs go to PROVISIONING but Spark pods never appear.

**Check**:
```bash
kubectl cluster-info
docker logs lakehouse-orchestrator --tail 200 | grep -i "kube\|tls\|host"
```

**Fixes**:
- Ensure `~/.kube/config` exists and is valid
- Ensure local K8s cluster is running
- Keep `K8S_HOST_ALIAS=host.docker.internal` in `.env`
- Keep `K8S_SKIP_TLS_VERIFY=true` for local development

---

## Spark Pods Stuck in Pending

**Symptoms**: K8s pods for Spark jobs show `Pending` status.

**Check**:
```bash
kubectl get pods -n lakehouse-jobs
kubectl describe pod -n lakehouse-jobs <pod-name> | grep -A5 "Events"
```

**Fixes**:
- Reduce resource requests in `.env`:
  ```
  DEFAULT_CPU_REQUEST=100m
  DEFAULT_CPU_LIMIT=500m
  DEFAULT_MEMORY_REQUEST=256Mi
  DEFAULT_MEMORY_LIMIT=1Gi
  ```
- Check cluster capacity: `kubectl top nodes`
- Ensure namespace exists: `kubectl get ns lakehouse-jobs`

---

## Spark Jobs FAIL Immediately

**Symptoms**: Job transitions PENDING → QUEUED → PROVISIONING → RUNNING → FAILED quickly.

**Check**:
```bash
# Get pod logs
kubectl logs -n lakehouse-jobs <pod-name> -c spark-<jobid8>

# Check if script exists in MinIO
curl -s -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8004/api/v1/storage/buckets/lakehouse-scripts/objects?prefix=etl/" | jq .
```

**Fixes**:
- Ensure the entrypoint script exists in MinIO (run `make seed`)
- Check S3 connectivity from the Spark container
- Verify `RUNTIME_S3_ENDPOINT` resolves correctly

---

## Missing Logs

**Symptoms**: Job logs endpoint returns empty results.

**Check**:
```bash
curl -s http://localhost:3100/ready
docker logs lakehouse-loki --tail 100
docker logs lakehouse-log-service --tail 100
```

**Fixes**:
- Verify Loki is healthy
- Ensure `ENABLE_FLUENT_BIT_SIDECAR=true` in orchestrator config
- Check if Spark container produced log file (logs to `/var/log/spark/`)
- Wait a few seconds after job completion for log shipping

---

## Database Connection Errors

**Symptoms**: Service logs show connection refused or authentication errors.

**Check**:
```bash
docker exec lakehouse-postgres pg_isready -U lakehouse -d lakehouse
docker logs lakehouse-job-service --tail 100
```

**Fixes**:
- Re-initialize schema: `make db-init`
- Reset schema (destructive): `make db-reset`
- Check `POSTGRES_PASSWORD` matches in `.env` and compose

---

## Services Fail to Start

**Symptoms**: Docker containers exit immediately or fail healthcheck.

**Check**:
```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}"
docker logs <container-name> --tail 50
```

**Fixes**:
- Build images first: `make build`
- Check dependency services are healthy before starting application services
- Verify port conflicts: `lsof -i :8001` (check all ports)

---

## Kafka Topics Not Created

**Symptoms**: Orchestrator logs show "topic not found" errors.

**Check**:
```bash
docker exec lakehouse-kafka kafka-topics --bootstrap-server localhost:9092 --list
```

**Fix**:
- Kafka has `KAFKA_AUTO_CREATE_TOPICS_ENABLE=true` - topics are created on first use
- Restart the orchestrator: `docker restart lakehouse-orchestrator`

---

## Grafana Dashboard Empty

**Symptoms**: Dashboard shows "No Data" for all panels.

**Check**:
```bash
# Verify Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Check datasource
curl -s -u admin:admin http://localhost:3000/api/datasources | jq '.[].name'
```

**Fixes**:
- Wait 30-60 seconds after stack start for metrics to populate
- Check Prometheus target health at http://localhost:9090/targets
- Verify Grafana datasources are provisioned

---

## Full Reset

When all else fails:

```bash
make clean
make build
make build-spark
make up
# Wait for all containers to be healthy
make seed
```
