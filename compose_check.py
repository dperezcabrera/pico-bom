"""The train's teeth: every module in the constraints file installs together
and a composed application actually boots and answers.

Hermetic on purpose: sqlite for the database, memory broker for celery,
no kafka/rabbitmq/redis servers (their modules still load and register).
Run inside a venv created from the constraints file."""

import asyncio
import sys

import httpx
from fastapi import FastAPI
from pico_ioc import DictSource, component, configuration, init
from pico_fastapi import controller, get

CONFIG = {
    "fastapi": {"title": "bom-check"},
    "database": {"url": "sqlite+aiosqlite:///:memory:"},
    "caching": {"enabled": True},
    "resilience": {"enabled": True},
    "celery": {"broker_url": "memory://", "backend_url": "cache+memory://"},
    "scheduling": {"enabled": True},
    "otel": {"traces_exporter": "none"},
    "auth_client": {"enabled": False, "issuer": "http://bom", "audience": "bom"},
    "server_auth": {"issuer": "http://bom", "audience": "bom"},
    "actuator": {"info": {"app": "bom-check"}},
    "http": {"clients": {}},
}

MODULES = [
    "pico_fastapi",
    "pico_sqlalchemy",
    "pico_pydantic",
    "pico_caching",
    "pico_resilience",
    "pico_httpx",
    "pico_scheduling",
    "pico_celery",
    "pico_actuator",
    "pico_otel",
    "pico_client_auth",
    "pico_server_auth",
    "pico_ioc.event_bus",
]


@controller(prefix="/api/bom")
class BomController:
    @get("/ping")
    async def ping(self):
        return {"train": "ok"}


@component
class Probe:
    def alive(self) -> bool:
        return True


def main() -> int:
    # the messaging modules must at least import cleanly from the pinned set
    import pico_data_redis  # noqa: F401
    import pico_kafka  # noqa: F401
    import pico_rabbitmq  # noqa: F401
    import pico_testing  # noqa: F401

    container = init(
        modules=[*MODULES, sys.modules[__name__]],
        config=configuration(DictSource(CONFIG)),
    )
    assert container.get(Probe).alive()
    app = container.get(FastAPI)

    async def call(path: str) -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://bom") as client:
            return await client.get(path)

    ping = asyncio.run(call("/api/bom/ping"))
    assert ping.status_code == 200 and ping.json() == {"train": "ok"}, ping.text

    health = asyncio.run(call("/actuator/health"))
    assert health.status_code == 200, health.text
    print(f"health: {health.json()['status']}")

    jwks = asyncio.run(call("/api/v1/auth/jwks"))
    assert jwks.status_code == 200 and jwks.json()["keys"], jwks.text

    container.shutdown()
    print("BOM OK: 18 modulos instalados y compuestos, app arrancada y respondiendo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
