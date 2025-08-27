# SurePetcare API Client

This repository provides a Python client for accessing the [SurePetcare API](https://app-api.beta.surehub.io/index.html?urls.primaryName=V1).  

The project is inspired by [benleb/surepy](https://github.com/benleb/surepy), but aims for improved separation of concerns between classes, making it easier to extend and support the production, v1 and v2 SurePetcare API.

## Supported devices
* Hub
* Pet door
* Feeder Connect
* Dual Scan Connect
* Dual Scan Pet Door
* poseidon Connect
* No ID Dog Bowl Connect

## Contributing
**Important:** Store your credentials in a `.env` file (see below) to keep them out of the repository.

Before pushing validate the changes with: `pre-commit run --all-files`..

### Issue with missing data
Best approach is to enable debug logging and provide relevant logs. Each call to the API logged before mapped to the package internal structure.
If from `hass-surepetcare` enable in configuration.yaml and go into logs -> home assistant core and show raw logs.
```
logger:
  default: info
  logs:
    surepetcare: debug
```