# Contributing

Guidelines for contributing to the DataHarbour Project.

---

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Install Python 3.11+
4. Install dependencies for the service you're working on:

```bash
cd services/job-service
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
```

---

## Project Structure

```
.
├── docs/                    # Documentation (MkDocs)
├── infra/                   # Docker Compose + K8s manifests
├── scripts/                 # Database init + seed scripts
├── services/                # Application microservices
│   ├── job-service/
│   ├── metadata-service/
│   ├── log-service/
│   ├── storage-service/
│   └── orchestrator/
└── spark-images/            # Spark runtime Docker image + sample jobs
```

---

## Running Tests

```bash
# All services
make test

# Individual service
make test-job-service
make test-metadata-service
make test-log-service
make test-storage-service
make test-orchestrator
```

---

## Code Style

- Python 3.11+ features are encouraged
- Use type hints for function signatures
- Follow existing patterns in each service
- Keep imports sorted (stdlib → third-party → local)

---

## Adding a New Service

1. Create directory under `services/<name>/`
2. Add `Dockerfile`, `requirements.txt`, `app/main.py`
3. Add to `infra/docker-compose.dev.yaml`
4. Add K8s manifests in `infra/k8s/`
5. Add tests under `services/<name>/tests/`
6. Update Makefile targets
7. Add documentation page in `docs/services/`

---

## Adding a Spark Job

1. Write your PySpark script
2. Save under `spark-images/jobs/`
3. Upload to MinIO: `mc cp <file> lakehouse/lakehouse-scripts/<path>`
4. Document in `docs/spark/writing-jobs.md`

---

## Documentation

Documentation uses MkDocs with Material theme:

```bash
# Install docs dependencies
pip install -r requirements-docs.txt

# Preview locally
make docs-serve

# Build static site
make docs
```

---

## Pull Request Process

1. Create a feature branch from `master`
2. Make your changes
3. Ensure tests pass: `make test`
4. Ensure docs build: `make docs`
5. Submit a pull request with clear description
6. Reference any related issues

---

## Commit Messages

Follow conventional commit style:

```
feat: add schema validation to metadata service
fix: resolve Kafka connection timeout in orchestrator
docs: update quickstart guide
test: add storage service endpoint tests
```
