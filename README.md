# SurePetcare API Client

[![PyPI Version][pypi-shield]][pypi]
[![Python Version][python-shield]][pypi]
[![Docs][wiki-shield]][wiki]

[![Tests][build-shield]][build]
[![Coverage][codecov-shield]][codecov]
[![Downloads][pypi-downloads-shield]][pypi]
[![License][license-shield]](LICENSE.md)
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

## CLI
This repo also support (to some extent) cli commands. The cli can be installed with `uv sync --extra cli` and is not included by default.

To see available commands use:
```python
surepccli --help
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


[build-shield]: https://img.shields.io/github/actions/workflow/status/FredrikM97/py-surepetcare/test-and-coverage.yml?style=for-the-badge&label=Tests
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
