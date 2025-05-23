import asyncio
import json
import os
from datetime import datetime
from datetime import timedelta

from dotenv import load_dotenv

from surepy.client import SurePetcareClient


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

    # Fetch devices
    household_ids = [h["id"] for h in await client.get_households()]
    devices = await client.get_devices(household_ids)
    devices_data = [d.raw_data for d in devices]
    save_json(devices_data, "temp/contr_mock_devices.json")
    # Fetch products
    products_data = [await client.get_product(device.product_id, device.id) for device in devices]
    save_json(products_data, "temp/contr_mock_products.json")

    # Fetch pet household history
    pets = await client.get_households_pets()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    pets_history = [pet.history() for pet in pets]
    [
        (await history.fetch(from_date=yesterday.isoformat(), to_date=today.isoformat()))
        for history in pets_history
    ]
    save_json([history._data for history in pets_history], "temp/contr_mock_pets_history.json")

    # Fetch pets
    pets = []
    for household_id in household_ids:
        pets.extend(await client.get_pets(household_id))
    pets_data = [p._data for p in pets]
    save_json(pets_data, "temp/contr_mock_pets.json")

    print("\nPlease open a GitHub issue and attach the following files:")
    print(f"- {os.path.abspath('temp/contr_mock_devices.json')}")
    print(f"- {os.path.abspath('temp/contr_mock_products.json')}")
    print(f"- {os.path.abspath('temp/contr_mock_pets_history.json')}")
    print(f"- {os.path.abspath('temp/contr_mock_pets.json')}")
    print("Thank you for contributing!")

    await client.close()


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
