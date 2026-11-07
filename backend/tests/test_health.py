import pytest


class FakeConnection:
    def __init__(self, fail=False):
        self.fail = fail

    async def __aenter__(self):
        if self.fail:
            raise RuntimeError("Database unavailable")
        return self

    async def __aexit__(self, *args):
        return False

    async def execute(self, query):
        return None


class FakeEngine:
    def __init__(self, fail=False):
        self.fail = fail

    def connect(self):
        return FakeConnection(self.fail)


class FakeRedis:
    def __init__(self, fail=False):
        self.fail = fail

    async def ping(self):
        if self.fail:
            raise RuntimeError("Redis unavailable")
        return True

    async def aclose(self):
        pass


class FakeRedisFactory:
    fail = False

    @classmethod
    def from_url(cls, *args, **kwargs):
        return FakeRedis(cls.fail)


@pytest.mark.asyncio
async def test_liveness_returns_200(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_returns_200_when_dependencies_are_available(
    client, monkeypatch
):
    import app.api.health as health

    monkeypatch.setattr(health, "engine", FakeEngine())
    monkeypatch.setattr(health, "Redis", FakeRedisFactory)
    FakeRedisFactory.fail = False

    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize("dependency", ["database", "redis"])
async def test_readiness_returns_503_when_dependency_fails(
    client, monkeypatch, dependency
):
    import app.api.health as health

    monkeypatch.setattr(
        health,
        "engine",
        FakeEngine(fail=(dependency == "database")),
    )

    FakeRedisFactory.fail = dependency == "redis"
    monkeypatch.setattr(health, "Redis", FakeRedisFactory)

    response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"][dependency] == "error"
