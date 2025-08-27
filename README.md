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
First run `pip install -r dev-requirements.txt` to add dependencies for development
Please upload issue with data find in contribute/files with `python -m contribute.contribution`. This generates mock data that can be used to improve the library. Dont forget to add email and password in the .env file.
