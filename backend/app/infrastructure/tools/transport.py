import re
from abc import ABC, abstractmethod


class HttpTransport(ABC):
    """
    Abstraction over external HTTP calls.

    Returns a (status_code, payload_dict) tuple.
    Enables mocking external APIs in tests.
    """

    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> tuple[int, dict]:
        raise NotImplementedError


class HttpxTransport(HttpTransport):
    """
    HTTPX-backed transport for production use.
    """

    def __init__(self) -> None:
        import httpx

        self._client = httpx.AsyncClient()

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> tuple[int, dict]:

        response = await self._client.request(
            method,
            url,
            json=json,
            headers=headers,
            params=params,
        )

        try:
            payload = response.json()
        except Exception:
            payload = {"text": response.text}

        return response.status_code, payload


class SimulatedTransport(HttpTransport):
    """
    Demo transport that returns realistic success payloads for
    known external APIs so the platform is fully demonstrable
    without live infrastructure.

    Unrecognized requests return a 200 with a best-effort payload
    so read/mutate actions never block the lifecycle.
    """

    def __init__(self, *, failure_rate: float = 0.0) -> None:

        self.failure_rate = failure_rate

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> tuple[int, dict]:

        path = re.sub(r"^https?://[^/]+", "", url)

        import random

        if self.failure_rate > 0 and random.random() < self.failure_rate:
            return 500, {"error": "Simulated upstream failure."}

        if "/pods/" in path and path.endswith("/log"):
            return self._k8s_logs(path)
        if "/api/v1/namespaces/" in path and "/pods/" in path:
            return self._k8s_pod(path, json)
        if "/pods" in path and method == "GET":
            return self._k8s_pods(path)
        if "/deployments/" in path and method in ("POST", "PATCH"):
            return self._k8s_deployment(path, json)
        if "/api/now/table/incident" in path and method == "POST":
            return self._snow_create(json)
        if "/api/now/table/incident/" in path and method == "PATCH":
            return self._snow_update(path, json)
        if "/api/now/table/incident/" in path and method == "GET":
            return self._snow_get(path)
        if "/api/now/table/change_request" in path and method == "POST":
            return self._snow_change_request(json)
        if "instances.aws" in url or "/aws/" in path or "execute-api" in url:
            return self._aws(path, method, json)

        return 200, {"ok": True, "message": "Simulated success."}

    # ==========================================================
    # Kubernetes
    # ==========================================================

    def _pod_name(self, path: str) -> str:

        match = re.search(r"/pods/([^/]+)/log$", path)

        return match.group(1) if match else "payments-7d9b5c4f6-2xk9p"

    def _k8s_pods(
        self,
        path: str,
    ) -> tuple[int, dict]:

        return 200, {
            "apiVersion": "v1",
            "kind": "PodList",
            "items": [
                {
                    "metadata": {
                        "name": "payments-7d9b5c4f6-2xk9p",
                        "namespace": "default",
                    },
                    "status": {
                        "phase": "Running",
                        "containerStatuses": [
                            {
                                "name": "payments",
                                "ready": True,
                                "restartCount": 1,
                                "state": {"running": {"startedAt": "2026-07-30T09:12:04Z"}},
                            }
                        ],
                    },
                },
                {
                    "metadata": {
                        "name": "payments-7d9b5c4f6-4hjbq",
                        "namespace": "default",
                    },
                    "status": {
                        "phase": "Running",
                        "containerStatuses": [
                            {
                                "name": "payments",
                                "ready": True,
                                "restartCount": 0,
                                "state": {"running": {"startedAt": "2026-07-31T14:02:11Z"}},
                            }
                        ],
                    },
                },
            ],
        }

    def _k8s_pod(
        self,
        path: str,
        json: dict | None,
    ) -> tuple[int, dict]:

        return 200, {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": self._pod_name(path),
                "namespace": "default",
            },
            "status": {
                "phase": "Running",
                "conditions": [
                    {"type": "Ready", "status": "True"}
                ],
                "containerStatuses": [
                    {
                        "name": "payments",
                        "ready": True,
                        "restartCount": 1,
                    }
                ],
            },
        }

    def _k8s_logs(
        self,
        path: str,
    ) -> tuple[int, dict]:

        return 200, {
            "text": (
                "2026-07-31 14:01:58 INFO  payments starting\n"
                "2026-07-31 14:02:00 INFO  health check ok (latency 12ms)\n"
                "2026-07-31 14:02:03 WARN  request latency p99 210ms\n"
                "2026-07-31 14:02:05 INFO  readiness probe passed\n"
            )
        }

    def _k8s_deployment(
        self,
        path: str,
        json: dict | None,
    ) -> tuple[int, dict]:

        return 200, {
            "status": "ok",
            "message": "Deployment rollout triggered.",
            "details": {
                "url": path,
                "replicas": json.get("replicas") if json else None,
            },
        }

    # ==========================================================
    # ServiceNow
    # ==========================================================

    def _snow_create(
        self,
        json: dict | None,
    ) -> tuple[int, dict]:

        payload = json or {}

        return 201, {
            "result": {
                "sys_id": "inc001b3f2a",
                "number": "INC0010492",
                "short_description": payload.get("short_description", "Automated incident"),
                "description": payload.get("description"),
                "category": payload.get("category", "infrastructure"),
                "impact": payload.get("impact", "2"),
                "urgency": payload.get("urgency", "2"),
                "state": "1",
            }
        }

    def _snow_update(
        self,
        path: str,
        json: dict | None,
    ) -> tuple[int, dict]:

        payload = json or {}

        return 200, {
            "result": {
                "sys_id": self._snow_sys_id(path),
                "number": "INC0010492",
                "state": payload.get("state", "1"),
                "close_notes": payload.get("close_notes"),
                "close_code": payload.get("close_code", "Solved (Permanently)"),
            }
        }

    def _snow_get(
        self,
        path: str,
    ) -> tuple[int, dict]:

        return 200, {
            "result": {
                "sys_id": self._snow_sys_id(path),
                "number": "INC0010492",
                "short_description": "Automated incident",
                "state": "1",
                "impact": "2",
                "urgency": "2",
            }
        }

    def _snow_change_request(
        self,
        json: dict | None,
    ) -> tuple[int, dict]:

        payload = json or {}

        return 201, {
            "result": {
                "sys_id": "chg00c4a1e9",
                "number": "CHG0004892",
                "short_description": payload.get("short_description", "Automated change"),
                "risk": payload.get("risk", "moderate"),
                "state": "new",
            }
        }

    @staticmethod
    def _snow_sys_id(path: str) -> str:

        match = re.search(r"/incident/([^/]+)", path)

        return match.group(1) if match else "inc001b3f2a"

    # ==========================================================
    # AWS
    # ==========================================================

    def _aws(
        self,
        path: str,
        method: str,
        json: dict | None,
    ) -> tuple[int, dict]:

        return 200, {
            "ok": True,
            "resource": path.split("/")[-1] or "resource",
            "operation": method,
            "arn": "arn:aws:execute-api:us-east-1:000000000000:simulated/1",
        }

