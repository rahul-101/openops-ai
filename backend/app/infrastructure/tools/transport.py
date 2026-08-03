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
