# SurePetcare API Client

[![PyPI Version][pypi-shield]][pypi]
[![Python Version][python-shield]][pypi]
[![Docs][wiki-shield]][wiki]

[![Tests][build-shield]][build]
[![Coverage][codecov-shield]][codecov]
[![Downloads][pypi-downloads-shield]][pypi]
[![License][license-shield]](LICENSE)
[![Dev Container][devcontainer-shield]][devcontainer]

---

## About

Python client for interacting with the SurePetcare API:

https://app-api.beta.surehub.io/index.html?urls.primaryName=V1

Includes:
- Core async IO client (`surepcio`)
- CLI tool (`surepccli`)

For Home Assistant integration see:
https://github.com/FredrikM97/hass-surepetcare

## Library scope

The library owns authenticated API access, typed household/pet/device models,
API commands, event parsing, and low-level timeline matching helpers. Home
Assistant-specific entity catalogues and field evaluation live in the sibling
`hass-surepetcare` integration. This keeps the API client independent of a
consumer's entity platforms, metadata, discovery policy, and state lifecycle.

`HouseholdState` retains household polling behavior: it refreshes reports with
per-device failure isolation, fetches and paginates timeline history, commits the
strict `seen_id` cursor only after publication succeeds, and preserves retry
behavior. Consumers receive the existing device models and `TimelineEvent`
objects through callbacks; timeline objects and their API payloads are not wrapped
in a new observation framework. The timeline callback is used by a
consumer-owned evaluator before the existing event payload is published.

Device publisher failures are retried on the next poll using the refreshed model,
without another API request while its report is still current. An optional
`on_devices_updated()` callback reports completion of the device phase (including
isolated endpoint failures) before timeline delivery; event publishers receive
only actual automation payloads, never a `None` notification.

Timeline delivery is at-least-once, not atomic across callbacks. If an event's
publication fails partway through, its already-successful callbacks can run again
on retry. Consumers should apply state updates idempotently and use event IDs if
they need to deduplicate side effects. Fully delivered events are skipped during
in-process retries; a restart before cursor persistence can also replay events.
Initial history fetches approximately one day, including whole boundary pages
to seed current state; it is not a strict 24-hour filter.

```python
def publish_device(device):
    # Evaluate the refreshed typed API model in the consuming application.
    ...

def publish_timeline(event):
    # Evaluate the existing TimelineEvent without changing its API shape.
    ...

await state.refresh(
    publish=publish_device,
    publish_timeline=publish_timeline,
    publish_event=on_event,
)
```

Reading helpers return plain `(value, attributes)` tuples. An optional reading
of `None` means no observation; a tuple with a `None` value means explicit unknown.
Pet/tag/household matching remains
in `surepcio.entities.pet`, and bowl-resource validation remains in
`surepcio.entities.bowl`; neither module owns an entity catalogue. Device control
methods such as `set_control`, `set_tag`, `set_position`, and `set_profile`
continue to return API `Command` objects executed with `client.api`.

The CLI uses the same public matching/reading helpers and API commands as other
clients. It does not depend on Home Assistant field descriptors.

## CLI
This repo also support (to some extent) cli commands. The cli can be installed with `uv sync --extra cli` and is not included by default.

To see available commands use:
```python
surepccli - -help
```
However, most functionality requires login therefore use the

```python
surepccli account login <email> 
```
It is possible to fetch available households with:
```python
surepccli household
```

There is also support to store some properties in .env file. Check available properties to the household and device for more info.

## Supported devices
* Hub
* Pet door
* Feeder Connect
* Dual Scan Connect
* Dual Scan Pet Door
* poseidon Connect
* No ID Dog Bowl Connect

# Enjoy the integration?

Star ⭐ the repository to help others discover the integration.

[![Sponsor FredrikM97][github-sponsor-shield]][github-sponsor] [![Static Badge][buymeacoffee-shield]][buymeacoffee]

## Contributing

1. Before pushing validate the changes with: `pre-commit run --all-files`.. 
2. Run `uv sync --all-extras --dev` to install development dependencies from `uv.lock`.
3. Use `uv lock` when dependency constraints change and commit the updated `uv.lock`.
4. Run tests with `uv run pytest tests` and snapshot updates with `uv run pytest --snapshot-update tests`.
5. For a quick vulnerability check against the lockfile:
`uv export --frozen --all-extras --format requirements-txt --no-hashes -o requirements.lock.txt && uv tool run --from pip-audit pip-audit -r requirements.lock.txt`.
6. Start application and enable debug. The debug logs contain request data that can be provided with an issue and for snapshot testing.

Timeline test setup lives in `tests/surepcio/conftest.py`: a fresh client,
pet and bowl-device setup, and movement, consumption and weight-event factories.
Ready-made movement, feeding, drinking and pet-history fixtures cover common
scenarios; live movement events use the test's clock for household polling.
Factories only construct inputs; tests apply events and assert snapshots directly.
Keep scenario-specific mutations and expected exceptions in the test itself.
Shared API fixtures and snapshot serialization remain in `tests/conftest.py`.

[build-shield]: https://img.shields.io/github/actions/workflow/status/FredrikM97/py-surepetcare/ci.yml?style=for-the-badge&label=Tests
[build]: https://github.com/FredrikM97/py-surepetcare/actions

[codecov-shield]: https://img.shields.io/codecov/c/github/FredrikM97/py-surepetcare?style=for-the-badge&label=Coverage
[codecov]: https://codecov.io/gh/FredrikM97/py-surepetcare

[license-shield]: https://img.shields.io/github/license/FredrikM97/py-surepetcare.svg?style=for-the-badge

[devcontainer-shield]: https://img.shields.io/badge/Dev%20Container-Open-007ACC?style=for-the-badge&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/FredrikM97/py-surepetcare

[wiki-shield]: https://img.shields.io/badge/Docs-Wiki-41BDF5?style=for-the-badge
[wiki]: https://github.com/FredrikM97/py-surepetcare/wiki

[pypi-shield]: https://img.shields.io/pypi/v/py-surepetcare.svg?style=for-the-badge
[pypi]: https://pypi.org/project/py-surepetcare/

[pypi-downloads-shield]: https://img.shields.io/pypi/dm/py-surepetcare.svg?style=for-the-badge

[python-shield]: https://img.shields.io/pypi/pyversions/py-surepetcare.svg?style=for-the-badge

[github-sponsor-shield]: https://img.shields.io/badge/Sponsor-FredrikM97-EA4AAA?style=for-the-badge&logo=githubsponsors
[github-sponsor]: https://github.com/sponsors/FredrikM97

[buymeacoffee-shield]: https://img.shields.io/badge/Donate-Buy%20Me%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee
[buymeacoffee]: https://www.buymeacoffee.com/FredrikM97
