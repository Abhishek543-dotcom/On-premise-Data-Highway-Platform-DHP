"""
Tests for Orchestrator service.
"""
import json
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from app.config import Settings


class TestOrchestratorConfig:
    def test_default_settings(self):
        """Settings should have sensible defaults."""
        settings = Settings()
        assert settings.kafka_job_topic == "spark-job-submissions"
        assert settings.kafka_consumer_group == "job-orchestrator"
        assert settings.k8s_namespace == "lakehouse-jobs"
        assert settings.spark_image == "lakehouse-spark:3.5.0"
        assert settings.spark_service_account == "spark-runner"
        assert settings.ttl_seconds_after_finished == 3600

    def test_runtime_overrides(self):
        """Runtime URLs should override defaults when provided."""
        settings = Settings(
            runtime_job_service_url="http://host.docker.internal:8001",
            runtime_s3_endpoint="http://host.docker.internal:9000",
            runtime_kafka_brokers="host.docker.internal:29092",
        )
        assert settings.runtime_job_service_url == "http://host.docker.internal:8001"
        assert settings.runtime_s3_endpoint == "http://host.docker.internal:9000"
        assert settings.runtime_kafka_brokers == "host.docker.internal:29092"

    def test_resource_defaults(self):
        """Resource defaults should be configured."""
        settings = Settings()
        assert settings.default_cpu_request == "2"
        assert settings.default_cpu_limit == "4"
        assert settings.default_memory_request == "8Gi"
        assert settings.default_memory_limit == "16Gi"


class TestK8sJobManagerInit:
    @patch("app.k8s_manager.config")
    @patch("app.k8s_manager.client")
    def test_loads_kube_config_when_not_in_cluster(self, mock_client, mock_config):
        """Should load kubeconfig from file when not running in cluster."""
        mock_client.Configuration.get_default_copy.return_value = MagicMock(
            host="https://localhost:6443"
        )
        mock_client.Configuration.set_default = MagicMock()

        from app.k8s_manager import K8sJobManager

        with patch("app.k8s_manager.settings") as mock_settings:
            mock_settings.k8s_in_cluster = False
            mock_settings.k8s_host_alias = None
            mock_settings.k8s_skip_tls_verify = False
            mock_settings.k8s_namespace = "lakehouse-jobs"
            mock_settings.spark_service_account = "spark-runner"

            manager = K8sJobManager()
            mock_config.load_kube_config.assert_called_once()


class TestK8sJobCreation:
    @patch("app.k8s_manager.config")
    @patch("app.k8s_manager.client")
    def test_create_spark_job_builds_correct_name(self, mock_client, mock_config):
        """Job names should follow pattern spark-job-<id8>-r<retry>."""
        mock_client.Configuration.get_default_copy.return_value = MagicMock(
            host="https://localhost:6443"
        )
        mock_client.Configuration.set_default = MagicMock()
        mock_batch = MagicMock()
        mock_core = MagicMock()
        mock_client.BatchV1Api.return_value = mock_batch
        mock_client.CoreV1Api.return_value = mock_core
        # Mock namespace check to succeed
        mock_core.read_namespace.return_value = True
        mock_core.read_namespaced_service_account.return_value = True

        from app.k8s_manager import K8sJobManager

        with patch("app.k8s_manager.settings") as mock_settings:
            mock_settings.k8s_in_cluster = False
            mock_settings.k8s_host_alias = None
            mock_settings.k8s_skip_tls_verify = False
            mock_settings.k8s_namespace = "lakehouse-jobs"
            mock_settings.spark_service_account = "spark-runner"
            mock_settings.spark_image = "lakehouse-spark:3.5.0"
            mock_settings.enable_fluent_bit_sidecar = False
            mock_settings.internal_api_token = "test-token"
            mock_settings.runtime_job_service_url = "http://host:8001"
            mock_settings.job_service_url = "http://job-service:8000"
            mock_settings.runtime_s3_endpoint = "http://host:9000"
            mock_settings.s3_endpoint = "http://minio:9000"
            mock_settings.s3_access_key = "key"
            mock_settings.s3_secret_key = "secret"
            mock_settings.runtime_kafka_brokers = "host:29092"
            mock_settings.kafka_brokers = "kafka:9092"
            mock_settings.default_cpu_request = "250m"
            mock_settings.default_cpu_limit = "1000m"
            mock_settings.default_memory_request = "512Mi"
            mock_settings.default_memory_limit = "2Gi"
            mock_settings.ttl_seconds_after_finished = 3600

            manager = K8sJobManager()

            job_event = {
                "job_id": "abcd1234-5678-9012-3456-789012345678",
                "entrypoint": "s3://lakehouse-scripts/etl/test.py",
                "arguments": ["--date", "2026-03-28"],
                "spark_config": {},
                "retry_count": 0,
            }

            # mock the K8s API calls
            mock_batch.create_namespaced_job.return_value = MagicMock()

            result = manager.create_spark_job(job_event)
            assert result is not None
            mock_batch.create_namespaced_job.assert_called_once()


class TestConsumerMessageProcessing:
    @pytest.mark.asyncio
    async def test_process_message_calls_k8s(self):
        """Processing a message should create a K8s job and update status."""
        from app.consumer import JobConsumer

        consumer = JobConsumer()
        consumer.k8s_manager = MagicMock()
        consumer.k8s_manager.create_spark_job.return_value = "spark-job-abcd1234-r0"
        consumer.http_client = AsyncMock()
        consumer.http_client.put.return_value = MagicMock(
            status_code=200,
            raise_for_status=MagicMock(),
        )

        message = MagicMock()
        message.value = {
            "job_id": "test-job-123",
            "entrypoint": "s3://scripts/test.py",
            "arguments": [],
            "spark_config": {},
            "retry_count": 0,
        }

        await consumer._process_message(message)
        consumer.k8s_manager.create_spark_job.assert_called_once_with(message.value)
