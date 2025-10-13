# SurePetcare API Client

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

