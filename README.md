# SurePetcare API Client
[![PyPI version][pypi-shield]][pypi]
[![Python Version][python-shield]][pypi]
[![License][license-shield]](LICENSE.md)
[![Documentation Status][wiki-shield]][wiki]
[![PyPI Downloads][pypi-downloads-shield]][pypi]

[![Build Status][build-shield]][build]
[![Code Coverage][codecov-shield]][codecov]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

## About
This repository provides a Python client for accessing the [SurePetcare API](https://app-api.beta.surehub.io/index.html?urls.primaryName=V1).  

It consist of io support (surepcio) and a cli (surepccli).

For home assistant support use the [hass-surepetcare](https://github.com/FredrikM97/hass-surepetcare)

## Cli support
This repo also support (to some extent) cli commands. The cli is installed with pip install .[cli] and is not included by default. 

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

## Contributing
Before pushing validate the changes with: `pre-commit run --all-files`..
Run `pip install .[dev]` to add dependencies for development. Start application and enable debug. The debug logs contain the request data which can be provided with a issue and for snapshot testing.



[build-shield]: https://github.com/FredrikM97/py-surepetcare/actions/workflows/test-and-coverage.yml/badge.svg
[build]: https://github.com/FredrikM97/py-surepetcare/actions
[codecov-shield]: https://codecov.io/gh/FredrikM97/py-surepetcare/branch/main/graph/badge.svg
[codecov]: https://codecov.io/gh/FredrikM97/py-surepetcare
[license-shield]: https://img.shields.io/github/license/FredrikM97/py-surepetcare.svg
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/FredrikM97/py-surepetcare
[ha-versions-shield]: https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/FredrikM97/py-surepetcare/main/hacs.json&label=homeassistant&query=$.homeassistant&color=blue&logo=homeassistant
[releases-shield]: https://img.shields.io/github/release/FredrikM97/py-surepetcare.svg
[releases]: https://github.com/FredrikM97/py-surepetcare/releases
[wiki-shield]: https://img.shields.io/badge/docs-wiki-blue.svg
[wiki]: https://github.com/FredrikM97/py-surepetcare/wiki
[homeassistant]: https://my.home-assistant.io/redirect/hacs_repository/?owner=FredrikM97&repository=py-surepetcare&category=integration
[pypi-shield]: https://img.shields.io/pypi/v/py-surepetcare.svg
[pypi]: https://pypi.org/project/py-surepetcare/
[pypi-downloads-shield]: https://img.shields.io/pypi/dm/py-surepetcare.svg
[python-shield]: https://img.shields.io/pypi/pyversions/py-surepetcare.svg