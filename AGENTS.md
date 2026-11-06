# Library and CLI development guidance

## Architecture and compatibility

- Read [architecture and testing](README.md) and the existing
  [typing, fixture, and exception conventions](.github/copilot-instructions.md)
  before changing the affected implementation.
- `surepcio` owns async API access, typed models, commands, timeline parsing,
  polling, and low-level pet/tag/household/bowl matching helpers. `surepccli`
  consumes the same public APIs.
- Keep this library independent of Home Assistant. HA field descriptors,
  evaluation, discovery, restoration, and presentation belong to the consuming
  integration, not a second catalogue in this library.
- Preserve Python 3.13 compatibility as declared in
  [pyproject.toml](pyproject.toml), even when developing with a newer interpreter.
- Preserve public command contracts. Check CLI callers and, when available, the
  sibling Home Assistant integration when changing shared APIs. Its editable
  development dependency must not hide production release compatibility issues.

## Behavior to preserve

- Preserve polling, pagination, per-device failure isolation, and retry behavior.
  Advance the timeline cursor only after successful publication.
- Timeline delivery is at-least-once, not atomic across callbacks. Do not assume
  exactly-once delivery or remove retry behavior to avoid duplicate callbacks.
- Keep missing, unavailable, zero, and false values distinct. Do not mask malformed
  API data or failed requests with successful empty results.
- Use established domain exceptions from `surepcio.security.exceptions`.
  Preserve async cancellation and avoid blocking I/O in async paths.

## Making and verifying changes

- Develop first; defer running tests, formatters, linters, type checks, builds,
  snapshot updates, and pre-commit hooks until the user explicitly requests
  validation. Finishing an edit or a development turn is not permission to run
  checks. Do not run them automatically or in the background between edits.
- Continue adding or updating tests alongside code changes, but leave execution
  deferred. Report validation as deferred, not passed, until checks are requested.
- Read affected code and tests first. Reuse existing helpers and types rather
  than adding parallel abstractions.
- Make the smallest complete change, preserve unrelated worktree changes, and
  avoid unrelated refactors or dependency upgrades.
- Add regression tests for fixes and update directly affected documentation.
  Reuse shared fixtures and realistic API models rather than broad mocks; keep
  scenario-specific mutations and assertions in the test.
- When setup or validation is requested, run commands from this project directory:
  - Initial setup or dependency changes: `uv sync --all-extras --dev`.
  - Focused tests: `uv run pytest tests/surepcio` or
    `uv run pytest tests/surepccli`, narrowed to affected test files when possible.
  - Full tests: `uv run pytest tests`.
  - Pre-PR checks: `uv run pre-commit run --all-files`.
- During requested validation, start with affected tests and expand for shared-code changes. For cross-project
  contracts, also run relevant integration tests when its checkout is available.
- Review snapshot diffs against intended behavior; do not regenerate snapshots
  merely to make failing tests pass. Use repository-configured lint and type checks.
- Do not install new tooling or resync environments merely to inspect code or
  make documentation-only changes.
- Ask before materially ambiguous behavior changes or destructive operations.
  Never use live accounts, devices, or credentials for validation without approval.
- Review the final diff and report exact checks run, failures, and unverified
  behavior. Do not claim checks passed without running them.
