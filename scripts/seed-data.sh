#!/bin/bash
# seed-data.sh - Seed initial data for development
# Uses the minio/mc Docker image to avoid local installation issues.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
JOBS_DIR="${PROJECT_DIR}/spark-images/jobs"

# Detect network name (default for this project)
NETWORK="${DOCKER_NETWORK:-lakehouse-network}"
MINIO_HOST="${MINIO_DOCKER_HOST:-minio:9000}"
MINIO_ACCESS_KEY="${S3_ACCESS_KEY:-dev-access-key-change-me}"
MINIO_SECRET_KEY="${S3_SECRET_KEY:-dev-secret-key-change-me}"

echo "=== Seeding MinIO via Docker mc client ==="
echo "    Network: ${NETWORK}"
echo "    MinIO:   ${MINIO_HOST}"

docker run --rm \
  --network "${NETWORK}" \
  --entrypoint /bin/sh \
  -v "${JOBS_DIR}:/jobs:ro" \
  minio/mc -c "
    mc alias set lakehouse http://${MINIO_HOST} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY} &&
    mc mb --ignore-existing lakehouse/lakehouse-warehouse &&
    mc mb --ignore-existing lakehouse/lakehouse-raw &&
    mc mb --ignore-existing lakehouse/lakehouse-scripts &&
    mc mb --ignore-existing lakehouse/lakehouse-logs &&
    echo '=== Buckets ready ===' &&
    mc cp /jobs/sample_etl.py lakehouse/lakehouse-scripts/etl/sample_etl.py &&
    mc cp /jobs/sample_etl.py lakehouse/lakehouse-scripts/etl/sales_transform.py &&
    mc cp /jobs/batch10/job_1.py lakehouse/lakehouse-scripts/batch10/job_1.py &&
    mc cp /jobs/batch10/job_2.py lakehouse/lakehouse-scripts/batch10/job_2.py &&
    mc cp /jobs/batch10/job_3.py lakehouse/lakehouse-scripts/batch10/job_3.py &&
    mc cp /jobs/batch10/job_4.py lakehouse/lakehouse-scripts/batch10/job_4.py &&
    mc cp /jobs/batch10/job_5.py lakehouse/lakehouse-scripts/batch10/job_5.py &&
    mc cp /jobs/batch10/job_6.py lakehouse/lakehouse-scripts/batch10/job_6.py &&
    mc cp /jobs/batch10/job_7.py lakehouse/lakehouse-scripts/batch10/job_7.py &&
    mc cp /jobs/batch10/job_8.py lakehouse/lakehouse-scripts/batch10/job_8.py &&
    mc cp /jobs/batch10/job_9.py lakehouse/lakehouse-scripts/batch10/job_9.py &&
    mc cp /jobs/batch10/job_10.py lakehouse/lakehouse-scripts/batch10/job_10.py &&
    echo '=== Seed data complete ===' &&
    echo 'Uploaded scripts:' &&
    mc ls lakehouse/lakehouse-scripts/ --recursive
  "
