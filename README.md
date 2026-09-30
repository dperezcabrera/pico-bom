# pico-bom

One answer to "which versions of the pico packages do I install together?".

Each file in this repository is a **release train**: a pinned set of every [pico](https://github.com/dperezcabrera/pico-ioc) package, validated as a whole. The packages are released independently, but the train is what gets tested composing into one application - the same guarantee a Spring Boot parent BOM gives, expressed as a pip constraints file.

## Usage

Pass the train as a constraints file and list only what you use:

```bash
pip install \
  -c https://raw.githubusercontent.com/dperezcabrera/pico-bom/main/2026.13.txt \
  pico-boot pico-fastapi pico-sqlalchemy
```

Constraints do not install anything by themselves: they pin whatever you name (and nothing else) to the validated version.

## Trains

| Train | Highlights |
|---|---|
| [2026.13](2026.13.txt) | pico-fastapi 0.4.3: FastAPI >= 0.142 ships built-in OpenTelemetry; `fastapi.telemetry` now defaults to `{"auto_configure": False}` so FastAPI never adds a second exporter next to pico-otel's |
| [2026.12](2026.12.txt) | Dependency floors that work: 16 patch releases raise every declared floor to what the module's suite proves (e.g. pico-ioc >= 2.3.3 fleet-wide, SQLAlchemy >= 2.0.46, celery >= 5.5), and every module's CI now runs the suite with its floors pinned |
| [2026.11](2026.11.txt) | pico-sqlalchemy 0.5.2 (depends on `sqlalchemy[asyncio]`: SQLAlchemy 2.1 no longer installs `greenlet` implicitly and 0.5.1 failed at import on fresh installs) |
| [2026.10](2026.10.txt) | pico-fastapi 0.4.1 (the `session` extra installs `itsdangerous` instead of `starlette-session`, which capped the whole install at `starlette<1`) |
| [2026.09](2026.09.txt) | pico-ioc 2.5.1 (config interpolation errors no longer swallowed as an absent prefix), pico-fastapi 0.4.0 (controller discovery and request-scope cleanup off pico-ioc internals), pico-client-auth 0.7.0 (`JWKSClient` exported as a replaceable seam) |
| [2026.07](2026.07.txt) | pico-ioc 2.3.4 (idempotent shutdown, config expand_env), pico-testing 0.2.0 fleet-wide, sqlalchemy 0.5.1 (ASGI-safe DDL hooks), PyJWT auth pair |

## Coverage

A train pins every published pico library - today 18 packages, from `pico-ioc` to the messaging and auth modules. CI installs exactly the packages listed in the train file, so adding a line to a train is all it takes to bring a new module under validation.

Deliberately outside the train:

- Applications that consume the libraries (`pico-auth`, `pico-skills-registry`): they version on their own and pin a train like any other user.
- Tooling that is not a Python package (`pico-initializer`, `pico-skills`, `pico-learn`, `pico-examples`): they follow the newest train instead of being part of it.
- `pico-agent`: deprecated, final release 0.2.1, never part of a train.

## What "validated" means

- CI installs the full set from PyPI into a clean environment and boots a composed application (13 modules in one container: HTTP, persistence, caching, resilience, scheduling, celery, auth, actuator, otel), asserting real responses from `/api`, `/actuator/health` and the JWKS endpoint - see [compose_check.py](compose_check.py).
- Before any package reaches PyPI, the ecosystem gate additionally exercises a flagship application against real infrastructure (PostgreSQL, Redis, RabbitMQ, Kafka).

A new train is published when the set changes meaningfully; old trains stay untouched, so a build pinned to a train is reproducible.

## License

MIT
