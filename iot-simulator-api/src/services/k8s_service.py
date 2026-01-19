import os
import logging
from typing import Tuple, List, Optional
from kubernetes import client, config

logger = logging.getLogger(__name__)


class K8sService:
    """Service for Kubernetes operations."""

    def __init__(self):
        self._load_config()
        self.v1 = client.CoreV1Api()
        self.namespace = os.getenv("K8s_NAMESPACE", "iot-sims")
        self.simulator_image = os.getenv("SIMULATOR_IMAGE", "None")

        if self.simulator_image == "None":
            logger.warning("SIMULATOR_IMAGE environment variable is not set.")
            raise ValueError("CRITICAL: SIMULATOR_IMAGE env var is missing!")

        logger.info(f"K8sService initialized with image: {self.simulator_image}")

    def _load_config(self):
        """Load Kubernetes configuration."""
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config.")
        except config.ConfigException:
            try:
                config.load_kube_config()
                logger.info("Loaded local kube-config.")
            except Exception as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                raise

    def create_pod(
        self,
        pod_name: str,
        sim_id: str,
        config_json: str,
        duration_minutes: int
    ) -> None:
        """Create a new simulation pod in Kubernetes."""
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "labels": {
                    "app": "iot-simulator",
                    "simulation_id": sim_id
                }
            },
            "spec": {
                "restartPolicy": "Never",
                "activeDeadlineSeconds": duration_minutes * 60,
                "containers": [{
                    "name": "simulator",
                    "image": self.simulator_image,
                    "imagePullPolicy": "IfNotPresent",
                    "env": [
                        {"name": "SIMULATOR_CONFIG_JSON", "value": config_json}
                    ]
                }]
            }
        }

        logger.debug(f"Pod Manifest: {pod_manifest}")
        self.v1.create_namespaced_pod(namespace=self.namespace, body=pod_manifest)
        logger.info(f"Created Pod {pod_name} in namespace {self.namespace}")

    def get_pod_status(self, pod_name: str) -> Tuple[str, List[str]]:
        """Get pod status and logs."""
        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=self.namespace)
            pod_status = pod.status.phase

            log_response = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=self.namespace,
                tail_lines=50
            )
            logs = log_response.split('\n') if log_response else []

            return pod_status, logs

        except client.exceptions.ApiException as e:
            if e.status == 404:
                return "Deleted/Expired", []
            logger.error(f"Error reading pod {pod_name}: {e}")
            return "K8s Error", []

    def delete_pod(self, pod_name: str) -> bool:
        """Delete a pod. Returns True if deleted, False if already gone."""
        try:
            self.v1.delete_namespaced_pod(
                name=pod_name,
                namespace=self.namespace,
                body=client.V1DeleteOptions(grace_period_seconds=0)
            )
            logger.info(f"Deleted Pod {pod_name}")
            return True
        except client.exceptions.ApiException as e:
            if e.status == 404:
                logger.info(f"Pod {pod_name} was already gone")
                return False
            raise

    def check_connection(self) -> bool:
        """Check if Kubernetes is accessible."""
        try:
            self.v1.list_namespaced_pod(namespace=self.namespace, limit=1)
            return True
        except Exception as e:
            logger.error(f"K8s connection check failed: {e}")
            return False


# Singleton instance
_k8s_service: Optional[K8sService] = None


def get_k8s_service() -> K8sService:
    """Get or create K8sService singleton."""
    global _k8s_service
    if _k8s_service is None:
        _k8s_service = K8sService()
    return _k8s_service
