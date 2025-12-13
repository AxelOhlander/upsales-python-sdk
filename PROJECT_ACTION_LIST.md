# Upsales Python SDK – Project Analysis & Action List

Last reviewed: 2025‑12‑12

This document summarizes the current stack/architecture and lists concrete improvement actions.
Priorities are rough: **P0 = correctness/blocker**, **P1 = high‑value**, **P2 = nice‑to‑have/cleanup**.

---

## 1. Stack & Architecture (Snapshot)

- **Language/runtime**: Python **3.13+** (uses PEP 695 type parameters, pattern matching, asyncio).
- **HTTP**: `httpx.AsyncClient` wrapped by `upsales/http.py:HTTPClient` with Tenacity retry on 429.
- **Models**: Pydantic v2 models in `upsales/models/` built on `BaseModel` and `PartialModel`.
  - Read‑only fields marked with `Field(frozen=True)`.
  - Update payload helpers: `to_update_dict`, `to_api_dict`, `to_update_dict_minimal`.
  - TypedDict + `Unpack` used for edit/update IDE autocomplete.
- **Resources**: Endpoint managers in `upsales/resources/` inherit `BaseResource[T,P]` providing CRUD, list/search, bulk ops.
- **Client**: `Upsales` instantiates `HTTPClient` and eagerly constructs all resources.
- **CLI**: `upsales/cli.py` generates models/resources and runs validators; relies on real API data + scripts under `scripts/`.
- **Testing**:
  - Unit tests with `pytest`, `pytest-asyncio`, `pytest-httpx`.
  - Integration tests with `vcrpy` + cassettes.
- **Docs**: MkDocs Material site under `docs/`.

Overall the structure is clean and modern, and the generator/testing workflow is unusually thorough for an SDK. The main gaps are around packaging hygiene and HTTP edge‑cases (binary / empty responses).

---

## 2. Action List

### HTTP Layer & Correctness

1. **P0 – Add binary / non‑JSON / empty‑body response support to `HTTPClient`.**  
   **Observation**: `HTTPClient.request()` always parses JSON into `dict`, but resources like `EsignFunctionResource.download()` and `VoiceResource.get_recording()` require raw bytes. Also 204/empty bodies would break `response.json()`.  
   **Impact**: Some endpoints are currently unimplementable or broken; doc/implementation mismatch.  
   **Suggestion**:
   - Extend `request()` with a `response_type: Literal["json","bytes","text","response"] = "json"` (or auto‑detect via `Content-Type`).
   - If `response_type="bytes"`, return `response.content`; if `"text"`, return `response.text`; if empty body, return `{}`/`None`.
   - Update `upsales/resources/esign_function.py` and `upsales/resources/voice.py` to use `"bytes"` and add unit tests.

2. **P1 – Make auth refresh concurrency‑safe.**  
   **Observation**: `_auth_refresh_attempted` is a single boolean on `HTTPClient`, shared across concurrent requests.  
   **Impact**: Two parallel 401s can cause one request to skip refresh and fail.  
   **Suggestion**:
   - Track refresh attempt per request (local var), or
   - Guard refresh with an async lock and a “refresh in flight” check, similar to `AuthenticationManager`.

3. **P1 – Improve retry policy beyond 429.**  
   **Observation**: Tenacity retries only on `RateLimitError`; transport timeouts / transient 5xx are not retried.  
   **Impact**: Reduced robustness in real networks.  
   **Suggestion**:
   - Retry on `httpx.TransportError`, `httpx.TimeoutException`, and optionally `ServerError`.
   - Respect `Retry-After` header on 429 when present.
   - Consider jittered backoff to avoid thundering herd.

4. **P1 – Align connection pool limits with `max_concurrent`.**  
   **Observation**: `httpx.AsyncClient` is created without explicit `Limits`.  
   **Impact**: With `max_concurrent` near 200, connection pool defaults may become a hidden throttle.  
   **Suggestion**:
   - Pass `limits=httpx.Limits(max_connections=max_concurrent, max_keepalive_connections=max_concurrent)` and make it configurable.

5. **P2 – Fix minor endpoint retry path inconsistency.**  
   **Observation**: After token refresh, retry uses `endpoint` rather than normalized `path` with leading `/`.  
   **Impact**: Edge‑case bug for callers passing endpoints without `/`.  
   **Suggestion**: Recompute `path` for retry or normalize at method entry.

### Packaging & Dependency Hygiene

6. **P0 – Remove dev/test/tooling packages from runtime dependencies.**  
   **Observation**: `pyproject.toml` `[project].dependencies` includes `pytest`, `black`, `coverage`, `bandit`, `vcrpy`, and even transitive libs like `pluggy`, `iniconfig`, etc., none of which are imported by production code.  
   **Impact**: Heavier installs, larger attack surface, slower CI/user setup.  
   **Suggestion**:
   - Keep only runtime deps (likely: `httpx`, `pydantic`, `pydantic-settings`, `tenacity`, `typer`, `rich`, `python-dotenv`).
   - Move the rest to optional `dev` or `dependency-groups.dev`.
   - Add a small script or CI check to fail on unused runtime deps.

7. **P1 – Add `py.typed` to ship type hints (PEP 561).**  
   **Observation**: Package declares `Typing :: Typed` but no `upsales/py.typed`.  
   **Impact**: Downstream users may not get type checking.  
   **Suggestion**: Add `upsales/py.typed` and include it in Hatchling package data.

8. **P1 – Fill in real metadata and add LICENSE.**  
   **Observation**: `authors`, `repo_url`, `site_url`, etc. are placeholders; no `LICENSE` file in root.  
   **Impact**: Confusing for users and PyPI readiness.  
   **Suggestion**:
   - Update metadata in `pyproject.toml` and `mkdocs.yml`.
   - Add `LICENSE` (MIT text).

9. **P2 – Derive `__version__` from package metadata.**  
   **Observation**: `upsales/__init__.py` hardcodes version.  
   **Impact**: Drift risk on release.  
   **Suggestion**: Use `importlib.metadata.version("upsales")` or hatch version injection.

### Models & Resources Consistency

10. **P1 – Standardize where Update TypedDicts live.**  
    **Observation**: Some models define `{Model}UpdateFields` locally, others only reference `upsales/types.py` under `TYPE_CHECKING`.  
    **Impact**: Inconsistent contributor experience; generator outputs vary.  
    **Suggestion**:
    - Decide on one pattern (prefer local per‑model TypedDicts for proximity), update generator and affected models accordingly, and deprecate the other location.

11. **P1 – Resolve outdated TODOs in partial models.**  
    **Observation**: `upsales/models/role.py:PartialRole.fetch_full/edit()` say RolesResource is missing, but `roles.py` and `resources/roles.py` exist.  
    **Impact**: Broken or misleading APIs.  
    **Suggestion**: Implement these methods to call `self._client.roles.get/update` and remove TODOs.

12. **P1 – Decide and enforce acronym/naming convention alignment.**  
    **Observation**: `CLAUDE.md` requires acronyms treated as words (`ApiKey`, `HttpClient`), but current code uses forms like `HTTPClient`, `AuthenticationManager`, `ApikeysResource`, etc.  
    **Impact**: Contributor/generator confusion and a latent breaking‑change decision.  
    **Suggestion**:
    - Choose one rule as authoritative.  
    - If keeping current names, update `CLAUDE.md` and `scripts/standardize_naming.py` to match.  
    - If switching to “acronyms as words”, plan a major‑version rename with deprecation aliases.

13. **P1 – Audit `edit()`/update payload pattern to use `to_api_dict()` (or minimal updates).**  
    **Observation**: `CLAUDE.md` marks `to_api_dict()` as the preferred edit serializer for speed and alias handling. Some legacy models may still call `to_update_dict()` or pass raw kwargs.  
    **Impact**: Inconsistent behavior/perf and higher risk of sending frozen/aliased fields incorrectly.  
    **Suggestion**: Grep models for `async def edit` and standardize to `self.to_api_dict(**kwargs)` (or `to_update_dict_minimal` when required fields are known); update generator to enforce.

14. **P2 – Prefer `Field(default_factory=...)` for mutable defaults.**  
    **Observation**: Many models use `default=[]` / `default={}`. Pydantic v2 copies defaults, but default_factory is clearer.  
    **Impact**: Avoids confusion and aligns with common style.  
    **Suggestion**: Gradually switch in generator for new models; avoid mass refactor unless desired.

15. **P2 – Revisit validator alias semantics for required emails.**  
    **Observation**: `EmailStr` is `Annotated[str | None, ...]`, so required email fields can accept `None`.  
    **Impact**: Potentially weaker validation than intended.  
    **Suggestion**: Split into `EmailStr` (optional) and `RequiredEmailStr` (str only), adjust generator.

16. **P2 – Confirm multi‑field `sort` encoding with the API.**  
    **Observation**: `sort` can be `list[str]`, passed to httpx as repeated params.  
    **Impact**: If API expects comma‑joined string, multi‑sort may not work.  
    **Suggestion**: Add an integration test for multi‑sort on one endpoint; if needed, normalize list → `",".join(...)`.

17. **P2 – Reduce `Upsales` init overhead.**  
    **Observation**: `Upsales.__init__` imports and instantiates every resource eagerly.  
    **Impact**: Slower startup, heavier memory footprint.  
    **Suggestion**: Lazy properties or a registry to instantiate on first access.

### Tooling, CI, and Repo Hygiene

18. **P1 – Add CI (GitHub Actions) for lint/type/tests.**  
    **Observation**: No `.github/workflows/` present.  
    **Impact**: Regression risk and harder collaboration.  
    **Suggestion**: Add workflows to run `ruff`, `mypy`, `pytest` (unit only on PR; integration on manual/cron).

19. **P2 – Refresh `CLAUDE.md` to match current implementation.**  
    **Observation**: Sections still describe some core models/resources as TODO/placeholders and assume CI already exists.  
    **Impact**: Onboarding friction and conflicting guidance with `AGENTS.md`/docs.  
    **Suggestion**: Update placeholders, remove stale CI references or add CI first, and align terminology/naming with the chosen rule in item 12.

20. **P2 – Move/remove local scratch artifacts from root.**  
    **Observation**: Root contains `playground.py`, coverage/htmlcov/site outputs, caches, etc. (`.gitignore` covers them but they clutter).  
    **Impact**: Noise for contributors; risk of accidental commits.  
    **Suggestion**: Move scratch scripts to `ai_temp_files/` and keep build artifacts out of the repo tree.

21. **P2 – Keep docs accurate with implementation.**  
    **Observation**: Docs claim binary download/voice recording support that isn’t implemented.  
    **Impact**: User confusion.  
    **Suggestion**: After HTTPClient upgrade, update `docs/endpoint-map.md` and related guides; otherwise mark as unsupported.

22. **P2 – Reevaluate “free‑threaded mode” positioning.**  
    **Observation**: Docs emphasize GIL‑free parallelism for asyncio workloads; practical gains may be minimal for I/O‑bound async.  
    **Impact**: Marketing mismatch; expectation risk.  
    **Suggestion**: Tone down claims or add a short explanation of when it helps (threads / CPU‑bound callbacks).

23. **P2 – Add chunked bulk ops for very large ID lists.**  
    **Observation**: `bulk_update/delete` schedules one task per id at once.  
    **Impact**: High memory usage for huge batches.  
    **Suggestion**: Process IDs in chunks while keeping semaphore concurrency.

---

## 3. Suggested Next Focus Order

1. Implement **HTTPClient binary/empty response support** + fix `voice`/`esign_function`.
2. Clean **runtime dependencies** in `pyproject.toml`.
3. Fix **PartialRole TODOs**, audit `edit()` serializers, and standardize Update TypedDict pattern.
4. Decide **naming convention alignment** and refresh `CLAUDE.md`.
5. Add **CI + py.typed + LICENSE + real metadata**.

If you want, I can start on items (1) and (6) in a follow‑up patch.
