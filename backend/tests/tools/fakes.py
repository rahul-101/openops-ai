from app.infrastructure.tools.transport import HttpTransport


class FakeTransport(HttpTransport):
    """
    Mock transport that returns canned responses or records
    outgoing requests.
    """

    def __init__(
        self,
        status: int = 200,
        payload: dict | None = None,
    ) -> None:

        self.status = status
        self.payload = payload or {}
        self.calls: list[dict] = []

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: dict | None = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> tuple[int, dict]:

        self.calls.append(
            {
                "method": method,
                "url": url,
                "json": json,
                "headers": headers,
                "params": params,
            }
        )

        return self.status, self.payload


class FakeDatabaseAdapter:
    """
    Mock database adapter.
    """

    def __init__(
        self,
        rows: list[dict] | None = None,
        affected: int = 0,
    ) -> None:

        self.rows = rows or []
        self.affected = affected
        self.queries: list[str] = []

    async def query(
        self,
        sql: str,
        parameters: dict | None = None,
    ) -> list[dict]:

        self.queries.append(sql)
        return self.rows

    async def execute(
        self,
        sql: str,
        parameters: dict | None = None,
    ) -> int:

        self.queries.append(sql)
        return self.affected
