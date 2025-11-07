# Repository Guidelines

## Project Structure & Module Organization
- `upsales/`: core SDK (client, http, auth, exceptions, `cli.py`), plus `models/` (Pydantic v2 data models) and `resources/` (endpoint managers).
- `tests/`: `unit/`, `integration/`, and `cassettes/` (VCR fixtures). Pytest configured via `pyproject.toml`.
- `examples/`, `docs/`, `scripts/`: usage samples, documentation site (MkDocs), and utilities.
- Config roots: `pyproject.toml` (ruff, mypy, pytest, coverage), `mkdocs.yml`. Use `ai_temp_files/` for any temporary docs or one‑off scripts; any non‑permanent files should always go there (ignored by linters).

## Build, Test, and Development Commands
- Install dev deps: `uv sync --all-extras`
- Run tests: `uv run pytest` (coverage enabled by default; HTML at `htmlcov/index.html`)
- Lint/format: `uv run ruff format .` and `uv run ruff check . --fix`
- Type check: `uv run mypy upsales`
- Docs: `uv run mkdocs serve` (local) or `uv run mkdocs build`
- CLI (codegen): `uv run upsales generate-model users --partial`

## Coding Style & Naming Conventions
- Python 3.13+, 4‑space indent, line length 100 (`ruff` enforced). Use native type hints (`list`, `dict`, `|`) and 3.12+ type parameters (`class Foo[T]:`). Prefer pattern matching.
- Models: use Pydantic v2; mark read‑only with `Field(frozen=True)`; `edit()` accepts `TypedDict` via `Unpack` and calls `to_update_dict()`.
- Naming: SDK uses UI‑friendly resource names (e.g., `Company` over API `accounts`). Model field casing may reflect API; camelCase allowed under `upsales/models` (see `N815` ignore).

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`, `pytest-cov`, `vcrpy`.
- Discovery: files `test_*.py`; run subsets with `uv run pytest -k users`.
- Integration tests use VCR under `tests/cassettes/`; avoid real network in unit tests.
- Coverage: configured via `pyproject.toml`; docstring coverage target is 90% (`interrogate`).

## Commit & Pull Request Guidelines
- Commits: follow Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). Keep changes focused; avoid unrelated reformatting.
- PRs: clear description, rationale, linked issues, tests, and doc updates. Include: `ruff` clean, mypy passes, tests green with coverage, no secrets.

## Security & Configuration Tips
- Configure via environment (.env supported): `UPSALES_TOKEN`, `UPSALES_ENABLE_FALLBACK_AUTH`, `UPSALES_EMAIL`, `UPSALES_PASSWORD`. Never commit secrets.
- Temporary work policy: place all non‑permanent docs and one‑off scripts in `ai_temp_files/`. Do not scatter temp files elsewhere. Only update VCR cassettes when intentionally re‑recording.

## Agent‑Specific Notes
- Follow patterns in `upsales/models/base.py` and `upsales/resources/base.py` when adding endpoints.
- Prefer minimal, surgical diffs consistent with existing style and tooling.

## Temporary Files Policy
- Place all non‑permanent docs, scratch notes, data dumps, and one‑off scripts in `ai_temp_files/`.
- Examples: `ai_temp_files/scripts/tmp_*.py`, `ai_temp_files/notes/`, `ai_temp_files/session-YYYY-MM-DD/`.
- Exclusions: this folder is ignored by linters/type checks/tests; never import from it in production code.
- Data hygiene: never commit secrets; prefer small redacted samples; prune large/obsolete artifacts regularly.
- Cassettes: only update `tests/cassettes/` when intentionally re‑recording fixtures.
