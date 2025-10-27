from .account import account
from .account import household
from .device import devices
from .pet import pet
from surepccli.session import load_env_once
from surepccli.typer import AsyncTyper


app = AsyncTyper(help="SurePetcare CLI")
app.add_typer(account, name="account")
app.add_typer(household, name="household")
app.add_typer(devices, name="devices")
app.add_typer(pet, name="pet")


@app.callback()
def _bootstrap():
    load_env_once()


if __name__ == "__main__":
    app()
