# Upsales Python SDK – Project Analysis & Action List

Last reviewed: 2025-12-13 (updated with P2 completions)

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

3. ✅ **P1 – Improve retry policy beyond 429.** *(COMPLETED)*
   - Now retries on `RateLimitError`, `ServerError` (5xx), and `TransientError` (transport/timeout)
   - Added `TransientError` exception class for transient network failures
   - Respects `Retry-After` header on 429 (stored in `RateLimitError.retry_after`)
   - Uses jittered exponential backoff via custom `_wait_with_retry_after()` function
   - Wraps `httpx.TimeoutException` and `httpx.TransportError` in `TransientError`

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

9. ✅ **P2 – Derive `__version__` from package metadata.** *(COMPLETED)*
   - Now uses `importlib.metadata.version("upsales")` to get version dynamically
   - Falls back to `"0.1.0"` for development installs where metadata isn't available

### Models & Resources Consistency

10. ✅ **P1 – Standardize where Update TypedDicts live.** *(DECISION MADE)*
    **Decision**: Local per-model TypedDicts are the standard pattern.
    - 65 of 76 models (85%) already define TypedDicts locally (correct pattern)
    - 11 models import from `upsales/types.py` (legacy pattern)
    - CLI generator already outputs local TypedDict definitions
    - `upsales/types.py` is deprecated; new models should define TypedDicts locally
    - Migration: Low priority, legacy imports still work fine

11. ✅ **P1 – Resolve duplicate Role/PartialRole definitions and imports.** *(COMPLETED)*
    - Deleted `upsales/models/role.py` (the stub with NotImplementedError)
    - Updated imports in `user.py`, `metadata.py`, and tests to use `upsales.models.roles.PartialRole`
    - `upsales/models/roles.py` is now the single source of truth

12. ✅ **P1 – Decide and enforce acronym/naming convention alignment.** *(DECISION MADE)*
    **Decision**: Keep existing code naming (`HTTPClient`, `AuthenticationManager`), update CLAUDE.md.
    - Breaking change to rename existing classes would cause unnecessary churn
    - CLAUDE.md should match reality: HTTP, URL, API treated as acronyms in existing code
    - New code should follow existing patterns for consistency
    - Exception: `ApiKey` (model class) follows lowercase convention per existing implementation

13. ✅ **P1 – Audit `edit()`/update payload pattern to use `to_api_dict()` (or minimal updates).** *(AUDITED)*
    **Audit Results**:
    - **66 files**: Correctly use `to_api_dict()` ✅
    - **6 files**: Still use `to_update_dict()` variants (api_keys.py, pricelist.py, project_plan_priority.py, segments.py, order_stages.py, user.py)
    - **~70 PartialModel edit() methods**: Pass raw `**kwargs` directly (acceptable for PartialModels)
    **Assessment**: 92% compliance. Remaining 6 files work correctly, migration is low priority.

14. ✅ **P2 – Prefer `Field(default_factory=...)` for mutable defaults.** *(COMPLETED)*
    - Updated CLI generator (`cli.py`) to emit `Field(default_factory=list)` and `Field(default_factory=dict)` instead of `default=[]` / `default={}`
    - New models generated via CLI will use the safer `default_factory` pattern
    - Existing models not mass-refactored (work correctly with Pydantic v2's copy behavior)

15. ✅ **P2 – Revisit validator alias semantics for required emails.** *(COMPLETED)*
    - Added `RequiredEmailStr` type alias to `upsales/validators.py`
    - `validate_required_email()` function raises error on None or empty string
    - `EmailStr` remains for optional email fields (returns `str | None`)
    - `RequiredEmailStr` for required email fields (returns `str`, never None)

16. ✅ **P2 – Confirm multi‑field `sort` encoding with the API.** *(VERIFIED)*
    - Verified that httpx correctly encodes `list[str]` as repeated query params: `sort=name&sort=-id`
    - Added unit tests in `tests/unit/test_multi_sort_encoding.py`
    - No code changes needed - current implementation works correctly

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

19. ✅ **P2 – Refresh `CLAUDE.md` to match current implementation.** *(COMPLETED)*
    - Removed placeholder references, updated "100+ models implemented"
    - Added Continuous Integration section documenting GitHub Actions CI
    - Updated naming conventions to match existing code (`HTTPClient`, not `HttpClient`)
    - Aligned terminology with current implementation patterns

20. ✅ **P2 – Move/remove local scratch artifacts from root.** *(COMPLETED)*
    - Moved `playground.py` to `ai_temp_files/playground.py`
    - Updated `.gitignore` to reference new location
    - Root directory now cleaner for contributors

21. ✅ **P2 – Keep docs accurate with implementation.** *(COMPLETED)*
    - Updated `docs/endpoint-map.md`: E-signature download marked as "✅ Implemented"
    - Added "Downloading Binary Files" section to `docs/examples/advanced-patterns.md`
    - Updated `docs/index.md` with "Binary downloads" in features list
    - Documentation now accurately reflects binary download capabilities

22. ✅ **P2 – Reevaluate "free‑threaded mode" positioning.** *(COMPLETED)*
    - Updated README.md, docs/index.md, docs/reference.md with nuanced positioning
    - Changed "true parallelism" claims to "efficient concurrent execution"
    - Added explanation that asyncio already handles I/O concurrency well
    - Clarified free-threaded mode helps with CPU-bound callbacks and hybrid workloads
    - Updated docstrings in `base.py` bulk operations

23. ✅ **P2 – Add chunked bulk ops for very large ID lists.** *(COMPLETED)*
    - Added `chunk_size` parameter to `bulk_update()` and `bulk_delete()` in `base.py`
    - When specified, processes IDs in batches for memory efficiency
    - Semaphore concurrency still limits parallel requests within each chunk
    - Errors from all chunks are aggregated into single ExceptionGroup

---

## 3. Completed vs Remaining

### Completed (22 items)
- ✅ #1 HTTPClient binary/empty response support
- ✅ #2 Auth refresh concurrency safety (per-request tracking)
- ✅ #3 Improved retry policy (5xx, transport errors, Retry-After)
- ✅ #4 Connection pool limits alignment
- ✅ #5 Endpoint retry path normalization
- ✅ #6 Runtime dependency cleanup
- ✅ #7 py.typed marker file (with Hatch build config)
- ✅ #8 LICENSE file + metadata
- ✅ #9 Dynamic version from metadata
- ✅ #10 TypedDict location pattern decision (local preferred)
- ✅ #11 Role/PartialRole deduplication
- ✅ #12 Acronym naming convention decision (match existing code)
- ✅ #13 edit() to_api_dict audit (92% compliance)
- ✅ #14 default_factory for mutable defaults (CLI generator updated)
- ✅ #15 Email validator split (RequiredEmailStr added)
- ✅ #16 Multi-field sort encoding (verified working)
- ✅ #18 GitHub Actions CI
- ✅ #19 CLAUDE.md refresh
- ✅ #20 Scratch artifact cleanup
- ✅ #21 Docs accuracy (binary download support documented)
- ✅ #22 Free-threaded mode positioning (nuanced docs)
- ✅ #23 Chunked bulk ops (chunk_size parameter added)

### Remaining P2 Items (1 item)
- #17 Lazy resource initialization (deferred - complex architectural refactor)

---

## 4. Suggested Next Focus Order

**All P0, P1, and most P2 items are now complete!**

Only one item remains:

1. **P2 #17**: Lazy resource initialization
   - Deferred as a complex architectural refactor
   - Current eager initialization works correctly
   - Would require significant changes to `Upsales.__init__` and resource access patterns
   - Benefit: Faster startup, lower memory footprint
   - Risk: Could affect IDE autocomplete experience if not done carefully
