import asyncio
import json
import os
from datetime import datetime

from dotenv import load_dotenv

from surepetcare.client import SurePetcareClient
from surepetcare.household import Household

FILE_DIR = "contribute/files"


def save_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved mock data to {filename}")


async def async_main():
    load_dotenv()
    email = os.getenv("SUREPY_EMAIL")
    password = os.getenv("SUREPY_PASSWORD")

    if not email or not password:
        print("Please set SUREPY_EMAIL and SUREPY_PASSWORD in your .env file.")
        return

    client = SurePetcareClient()
    await client.login(email=email, password=password)

    # Fetch households (now returns list of Household objects)
    households = await client.api(Household.get_households())
    if not households:
        print("No households found.")
        await client.close()
        return

    all_devices = []
    all_products = []
    all_pets = []
    all_pets_history = []

    today = datetime.now().date()

    for household in households:
        # Fetch devices for this household
        devices = await client.api(household.get_devices())
        all_devices.extend(devices)

        # Fetch products for this household's devices
        products = [await client.api(Household.get_product(device.product_id, device.id)) for device in devices]
        all_products.extend(products)

        # Fetch pets for this household
        pets = await client.api(household.get_pets())
        all_pets.extend(pets)

        # Fetch pet history for this household's pets
    
        [
            (await client.api(pet.refresh()))
            for pet in pets
        ]
        all_pets_history.extend(pets)

    # Save all devices
    devices_data = [d.raw_data for d in all_devices]
    save_json(devices_data, f"{FILE_DIR}/contr_mock_devices.json")

    # Save all products
    save_json(all_products, f"{FILE_DIR}/contr_mock_products.json")

    # Save all pets history
    save_json([history._data for history in all_pets_history], f"{FILE_DIR}/contr_mock_pets_history.json")

    # Save all pets
    pets_data = [p._data for p in all_pets]
    save_json(pets_data, f"{FILE_DIR}/contr_mock_pets.json")

    print("\nPlease open a GitHub issue and attach the following files:")
    print(f"- {os.path.abspath(f'{FILE_DIR}/contr_mock_devices.json')}")
    print(f"- {os.path.abspath(f'{FILE_DIR}/contr_mock_products.json')}")
    print(f"- {os.path.abspath(f'{FILE_DIR}/contr_mock_pets_history.json')}")
    print(f"- {os.path.abspath(f'{FILE_DIR}/contr_mock_pets.json')}")
    print("Thank you for contributing!")

    await client.close()


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
