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

## Example Usage

```python
from dotenv import load_dotenv
import os
from surepetcare.client import SurePetcareClient

# Load credentials from .env file
load_dotenv(dotenv_path=".env")

email = os.getenv("SUREPY_EMAIL")
password = os.getenv("SUREPY_PASSWORD")

client = SurePetcareClient()
await client.login(email=email, password=password)
household_ids = [household['id'] for household in (await client.get_households())]
await client.get_devices(household_ids)
```
