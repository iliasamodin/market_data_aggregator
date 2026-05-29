# Market Data Aggregator

Market data collection and aggregation service for positional trading.
The service evaluates trading strategies across multiple instruments and timeframes,
and notifies the trader via Telegram when potential market entry conditions are met.

## Overview

The service periodically fetches technical analysis data from TradingView,
evaluates configurable groups of trading algorithms against each active ticker,
and sends a Telegram alert when all conditions in a group are satisfied simultaneously.

Key capabilities:

- **Multi-algorithm groups** — a signal fires only when every algorithm in a group evaluates to true (AND-conjunction), allowing complex multi-condition strategies to be expressed without code changes.
- **Cross-timeframe evaluation** — algorithms within a single group can operate on different timeframes. For example, an Envelope lower boundary breakout on 1M and a bullish price crossover above SMA20 on 1W can be combined into one group; both must be true for the signal to fire.
- **Per-ticker configuration** — each ticker is independently linked to one or more groups, with its own signal expiration window for deduplication.
- **Pluggable algorithms** — new strategies are added by registering a pure function in the strategy map; no changes to orchestration code are required.

## Architecture

The project follows **Hexagonal Architecture** (Ports & Adapters) and **Domain-Driven Design**.

```
src/
├── core/
│   ├── domain/          # Entities, value objects, domain strategies, constants
│   ├── application/     # Use cases, DTOs, exceptions
│   └── ports/           # Input and output port abstractions
├── adapters/
│   ├── primary/         # HTTP adapter (Robyn), authentication, routing
│   └── secondary/       # Repository and provider implementations (SQLAlchemy, TradingView, Telegram)
├── infrastructure/      # Database engine, ORM models, Alembic migrations, Telegram config
└── bootstrap/           # Composition root: DI container, app wiring, logging config
```

Dependency direction is strictly centripetal: `adapters` and `infrastructure` depend on `core`; `core` has no knowledge of adapters or infrastructure. `bootstrap` is the only layer allowed to import from all others.

### Domain layer

The domain layer contains the business logic that is independent of external system.

**Entities:**

| Entity | Role |
|---|---|
| `TickerEntity` | A tradable instrument with its exchange and active calculation configs |
| `GroupEntity` | An AND-conjunction of algorithm configs; owns the `is_triggered` method |
| `AlgorithmConfigEntity` | One algorithm instance with its timeframe, level, and optional moving-average type; owns the `is_triggered` dispatch to the strategy function |
| `SignalCalculationConfigEntity` | Links a ticker to a group; stores the deduplication window |
| `HistoricalSignalEntity` | A persisted record of a generated signal and its delivery status |

**Trading strategies:**

Strategies are pure functions registered in `STRATEGY_MAP`. Each function receives an `AlgorithmConfigEntity` and a `MarketDataSnapshotVO` and returns a boolean.

| Family | Algorithms |
|---|---|
| ADX | Consolidation transition, extreme trend, +DI/−DI growth/decline, DI bullish/bearish crossover |
| Envelope | Lower boundary breakout, upper boundary breakout |
| MACD | Signal line bullish crossover, signal line bearish crossover |
| RSI | Oversold/overbought reached, growth, decline |

### Multi-algorithm and cross-timeframe signal evaluation

A `GroupEntity` holds a list of `AlgorithmConfigEntity` references. When `group.is_triggered()` is called, it iterates over every algorithm config in the group and calls `algorithm_config.is_triggered(snapshot)` where `snapshot` is selected from a map keyed by timeframe. This means:

- Each algorithm config independently specifies its own timeframe.
- Market data for all required timeframes is fetched before evaluation begins.
- The group returns `True` only when **all** algorithm configs evaluate to `True` — regardless of whether they operate on the same or different timeframes.

Example: a group containing `RSI oversold on 1h` + `MACD bullish crossover on 4h` fires only when both conditions are true simultaneously. Adding a third condition (`ADX < 25 on 1d`) requires only a database record — no code change.

## Concurrency model

The service uses **threading** (`ThreadPoolExecutor`) rather than async/await. This is a deliberate architectural decision:

The application is not IO-bound in the classic web-service sense: it makes a bounded number of external API calls per evaluation cycle (one batch call per timeframe/screener pair to TradingView, one Telegram call per signal), and these calls are not continuous.

Threading was chosen over async for reliability:

- **No coroutine leak risk.** With threads, a hung external call blocks only its worker thread; the rest of the pool continues unaffected. With async, a blocking call in a coroutine stalls the entire event loop.
- **Predictable error isolation.** Each `Future` encapsulates its own exception; failures in one evaluation task do not propagate to others.
- **Simpler reasoning.** Strategy evaluation functions are pure and synchronous; wrapping them in coroutines would add complexity with no benefit.
- **Daemon threads.** A custom `DemonicThreadPoolExecutor` is used so that evaluation threads do not block process shutdown.

Market data fetches are submitted concurrently — one task per `(timeframe, screener)` pair — achieving parallel IO without async. Signal evaluations for individual ticker/config pairs are also submitted concurrently to the same pool, which means that adopting free-threading (no-GIL) in future Python versions will allow true simultaneous execution of signal calculations across multiple calculation configs without any changes to the application code.

## Signal deduplication

Before persisting and sending a new signal, the service queries `signal_history` for a recent `SENT` record for the same `calculation_config_id` within the configured `signal_expiration_timestamp` window. If one exists, the current evaluation cycle skips that ticker/group pair. This prevents repeated notifications for a condition that remains continuously true across multiple evaluation cycles.

## Project structure details

```
src/core/domain/
├── entities/            # Aggregate roots and entities
<!-- ├── value_objects/       # Immutable value objects (ExchangeVO, MarketDataSnapshotVO, IndicatorsSnapshotVO) -->
├── strategies/          # Pure strategy functions and STRATEGY_MAP registry
└── constants/           # Domain enumerations (AlgorithmEnum, TimeframeEnum, ScreenerEnum, ...)

src/core/application/
├── use_cases/           # SignalEvaluatorUseCase — orchestrates the full evaluation cycle
├── utils/               # exc_translator decorator, ModuleLoader, DemonicThreadPoolExecutor
└── exceptions/          # Typed exceptions for use-case, repository, and provider failures

src/adapters/primary/
└── http/
    ├── endpoints/       # Route handlers (one module per domain)
    └── auth.py          # Bearer API-key authentication handler

src/adapters/secondary/
├── repositories/        # SQLAlchemy Core implementations of output repository ports
└── providers/           # TradingView market data provider, Telegram notification provider

src/infrastructure/
├── database/
│   ├── models/          # SQLAlchemy ORM models
│   └── migrations/      # Alembic migration scripts
└── telegram/            # Telegram Bot API config

src/bootstrap/
├── di/                  # dependency-injector containers
├── web.py               # Robyn app, OpenAPI config, static spec loading
├── agg_router.py        # Aggregating router (wires DI + HTTP adapters)
└── main.py              # Entry point
```

## Tech stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| Web framework | Robyn |
| Database | PostgreSQL 17 |
| ORM, migrations | SQLAlchemy Core 2.x, Alembic |
| Market data | tradingview-ta |
| Notifications | Telegram Bot API |
| DI container | dependency-injector |
| Package manager | uv |
| Containerization | Docker, Docker Compose |

## Getting started

### Prerequisites

- Docker and Docker Compose
- A `.env` file with the required variables (see below)

### Environment variables

```env
# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=market_data
DB_USER=postgres
DB_PASSWORD=secret
DB_SCHEMA=trading

# HTTP server
HOST=0.0.0.0
PORT=1500
API_PREFIX=/api
API_AUTH_KEY=your-secret-api-key

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Logging
LOG_LEVEL=INFO
LOG_DIR=/app/logs
LOG_BACKUP_COUNT=30

# Docker bind mount
PATH_OF_BIND_MOUNT=/opt/market-data-aggregator
```

### Run with Docker Compose

```bash
docker compose up --build
```

This starts the database, runs Alembic migrations, then starts the application server.

### Run locally

```bash
uv sync
uv run python src/bootstrap/main.py
```

### Apply migrations

```bash
uv run alembic upgrade head
```

### API

All endpoints require Bearer authentication:

```
Authorization: Bearer <API_AUTH_KEY>
```

#### `POST /signal-evaluator/v1/execute`

Triggers a full evaluation cycle for all active tickers. Returns execution statistics.

```json
{
  "processed_configs_count": 4,
  "created_signals_count": 1,
  "sent_signals_count": 1
}
```

## OpenAPI spec generation

The Swagger security scheme requires a pre-generated spec file. After changing any HTTP endpoint, regenerate it:

```bash
uv run python scripts/generate_openapi.py
```

The file is also regenerated automatically before each commit via the `generate-openapi` pre-commit hook.
Install the hooks after cloning:

```bash
uv run pre-commit install
```
