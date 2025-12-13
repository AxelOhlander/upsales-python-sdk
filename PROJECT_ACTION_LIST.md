# Upsales Python SDK – Project Analysis & Action List

Last reviewed: 2025‑12‑13

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

1. ✅ **P0 – Add binary / non‑JSON / empty‑body response support to `HTTPClient`.** *(COMPLETED)*
   - Added `response_type: Literal["json","bytes","text","response"]` parameter to `request()`
   - Added `get_bytes()` convenience method for binary downloads
   - Handles 204/empty responses by returning `{}`
   - Updated `VoiceResource.get_recording()` and implemented `EsignFunctionResource.download()`

2. ✅ **P1 – Make auth refresh concurrency‑safe.** *(COMPLETED)*
   - Changed from instance-level `_auth_refresh_attempted` flag to per-request local variable tracking
   - Each request now independently tracks refresh attempts, avoiding race conditions

3. **P1 – Improve retry policy beyond 429.**
   **Observation**: Tenacity retries only on `RateLimitError`; transport timeouts / transient 5xx are not retried.
   **Impact**: Reduced robustness in real networks.
   **Suggestion**:
   - Retry on `httpx.TransportError`, `httpx.TimeoutException`, and optionally `ServerError`.
   - Respect `Retry-After` header on 429 when present.
   - Consider jittered backoff to avoid thundering herd.

4. ✅ **P1 – Align connection pool limits with `max_concurrent`.** *(COMPLETED)*
   - HTTPClient now passes `limits=httpx.Limits(max_connections=max_concurrent, max_keepalive_connections=max_concurrent)`

5. ✅ **P2 – Fix minor endpoint retry path inconsistency.** *(COMPLETED)*
   - Now normalizes path once at method entry and uses consistent `path` variable for retries

### Packaging & Dependency Hygiene

6. ✅ **P0 – Remove dev/test/tooling packages from runtime dependencies.** *(COMPLETED)*
   - Reduced runtime dependencies from 24 packages to 7 essential packages:
     - `httpx`, `pydantic`, `pydantic-settings`, `tenacity`, `python-dotenv`, `typer`, `rich`
   - Moved dev tools (pytest, black, vcrpy, coverage, etc.) to `[project.optional-dependencies].dev`
   - Updated author metadata from placeholder to actual values

7. ✅ **P1 – Add `py.typed` to ship type hints (PEP 561).** *(COMPLETED)*
   - Added `upsales/py.typed` marker file

8. ✅ **P1 – Fill in real metadata and add LICENSE.** *(COMPLETED)*
   - Added MIT LICENSE file
   - Updated author metadata in pyproject.toml

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

11. ✅ **P1 – Resolve duplicate Role/PartialRole definitions and imports.** *(COMPLETED)*
    - Deleted `upsales/models/role.py` (the stub with NotImplementedError)
    - Updated imports in `user.py`, `metadata.py`, and tests to use `upsales.models.roles.PartialRole`
    - `upsales/models/roles.py` is now the single source of truth

12. **P1 – Decide and enforce acronym/naming convention alignment.**
    **Observation**: `CLAUDE.md` requires acronyms treated as words (`ApiKey`, `HttpClient`), but current code uses forms like `HTTPClient`, `AuthenticationManager`, `ApikeysResource`, etc.
    **Impact**: Contributor/generator confusion and a latent breaking‑change decision.
    **Suggestion**:
    - Choose one rule as authoritative.
    - If keeping current names, update `CLAUDE.md` and `scripts/standardize_naming.py` to match.
    - If switching to "acronyms as words", plan a major‑version rename with deprecation aliases.

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

18. ✅ **P1 – Add CI (GitHub Actions) for lint/type/tests.** *(COMPLETED)*
    - Added `.github/workflows/ci.yml` with:
      - Triggers on push to main and pull requests
      - Python 3.13 with uv package manager
      - Runs `ruff check`, `ruff format --check`, `pytest tests/unit/`

19. **P2 – Refresh `CLAUDE.md` to match current implementation.**
    **Observation**: Sections still describe some core models/resources as TODO/placeholders and assume CI already exists.
    **Impact**: Onboarding friction and conflicting guidance with `AGENTS.md`/docs.
    **Suggestion**: Update placeholders, remove stale CI references or add CI first, and align terminology/naming with the chosen rule in item 12.

20. **P2 – Move/remove local scratch artifacts from root.**
    **Observation**: Root contains `playground.py`, coverage/htmlcov/site outputs, caches, etc. (`.gitignore` covers them but they clutter).
    **Impact**: Noise for contributors; risk of accidental commits.
    **Suggestion**: Move scratch scripts to `ai_temp_files/` and keep build artifacts out of the repo tree.

21. **P2 – Keep docs accurate with implementation.**
    **Observation**: Docs claim binary download/voice recording support that isn't implemented.
    **Impact**: User confusion.
    **Suggestion**: After HTTPClient upgrade, update `docs/endpoint-map.md` and related guides; otherwise mark as unsupported.

22. **P2 – Reevaluate "free‑threaded mode" positioning.**
    **Observation**: Docs emphasize GIL‑free parallelism for asyncio workloads; practical gains may be minimal for I/O‑bound async.
    **Impact**: Marketing mismatch; expectation risk.
    **Suggestion**: Tone down claims or add a short explanation of when it helps (threads / CPU‑bound callbacks).

23. **P2 – Add chunked bulk ops for very large ID lists.**
    **Observation**: `bulk_update/delete` schedules one task per id at once.
    **Impact**: High memory usage for huge batches.
    **Suggestion**: Process IDs in chunks while keeping semaphore concurrency.

---

## 3. Completed vs Remaining

### Completed (10 items)
- ✅ #1 HTTPClient binary/empty response support
- ✅ #2 Auth refresh concurrency safety (per-request tracking)
- ✅ #4 Connection pool limits alignment
- ✅ #5 Endpoint retry path normalization
- ✅ #6 Runtime dependency cleanup
- ✅ #7 py.typed marker file
- ✅ #8 LICENSE file + metadata
- ✅ #11 Role/PartialRole deduplication
- ✅ #18 GitHub Actions CI

### Remaining P1 Items (4 items)
- #3 Improved retry policy (5xx, transport errors)
- #10 Standardize TypedDict location
- #12 Acronym naming convention decision
- #13 Audit edit() to use to_api_dict()

### Remaining P2 Items (9 items)
- #9 Dynamic version from metadata
- #14 default_factory for mutable defaults
- #15 Email validator split
- #16 Multi-field sort encoding
- #17 Lazy resource initialization
- #19 CLAUDE.md refresh
- #20 Scratch artifact cleanup
- #21 Docs accuracy
- #22 Free-threaded mode positioning
- #23 Chunked bulk ops

---

## 4. Suggested Next Focus Order

1. **P1 Remaining**: Improve retry policy (#3) for production robustness
2. **P1 Remaining**: Decide naming conventions (#12) and update CLAUDE.md (#19)
3. **P1 Remaining**: Audit edit() serializers (#13) and standardize TypedDict location (#10)
4. **P2**: Documentation accuracy (#21) now that HTTPClient supports binary
5. **P2**: Dynamic version (#9) and other packaging polish
