from typing import Optional

import typer
from typer import Option

from surepccli.const import Envs
from surepccli.session import get_session_manager
from surepcio.devices.device import DeviceBase
from surepcio.enums import ProductId
from surepcio.household import Household


def _bad_param(msg: str):
    raise typer.BadParameter(msg)


def household_option():
    return Option(
        None,
        "--household-id",
        envvar=Envs.HOUSEHOLD_ID,
        help="Household ID.",
        show_envvar=True,
        callback=lambda c, p, v: v
        if v
        else _bad_param(
            "No household ID provided. Use --household-id or set HOUSEHOLD_ID environment variable."
        ),
    )


def device_id_option():
    return Option(
        None,
        "--device-id",
        envvar=Envs.SELECTED_DEVICE,
        help="Device ID.",
        show_envvar=False,
        callback=lambda c, p, v: v
        if v
        else _bad_param("No device selected. Use --device-id or 'surepccli devices list --store' first."),
    )


def pet_id_option():
    return Option(
        None,
        "--pet-id",
        envvar=Envs.SELECTED_PET,
        help="Pet ID.",
        show_envvar=False,
        callback=lambda c, p, v: v
        if v
        else _bad_param("No Pet selected. Use --pet-id or 'surepccli pet connect' first."),
    )


def product_id_option(optional: bool = False):
    return Option(
        None,
        "--product-id",
        "-p",
        envvar=Envs.SELECTED_PRODUCT_ID,
        help="Product ID.",
        show_envvar=False,
        callback=lambda c, p, v: v
        if v or optional
        else _bad_param("No product selected. Use --product-id or 'surepccli devices list --store' first."),
    )


def state_option(help: str = "", **kwargs) -> typer.Option:
    return Option(
        None,
        "--state",
        "-s",
        help=help,
        show_envvar=False,
        **kwargs,
    )


def print_table(rows, headers):
    """Reusable function to print a compact, aligned table."""
    col_widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
    header_line = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    typer.echo(header_line)
    typer.echo("-" * len(header_line))
    for row in rows:
        typer.echo(" | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row))))


async def _fetch_all_devices(household_id: str) -> list[DeviceBase]:
    async with get_session_manager() as sm:
        return await sm.client.api(Household({"id": household_id}).get_devices())


def _apply_filters(
    devices: list[DeviceBase],
    device_id: Optional[str] = None,
    product_id: Optional[str | ProductId] = None,
) -> list[DeviceBase]:
    if product_id:
        pid = str(product_id.value) if isinstance(product_id, ProductId) else str(product_id)
        devices = [d for d in devices if str(getattr(d.product_id, "value", d.product_id)) == pid]
    if device_id:
        devices = [d for d in devices if str(d.id) == str(device_id)]
    return devices


async def fetch_devices(
    household_id: str,
    device_id: Optional[str] = None,
    product_id: Optional[str | ProductId] = None,
) -> list[DeviceBase]:
    devices = await _fetch_all_devices(household_id)
    return _apply_filters(devices, device_id=device_id, product_id=product_id)


async def fetch_device(household_id: str, device_id: str) -> DeviceBase:
    for d in await _fetch_all_devices(household_id):
        if str(d.id) == str(device_id):
            async with get_session_manager() as sm:
                await sm.client.api(d.refresh())
            return d
    raise ValueError(f"Device {device_id} not found in household {household_id}.")


async def list_devices(
    household_id: str,
    product_id: Optional[str] = None,
) -> list[DeviceBase]:
    typer.echo(f"Listing devices for household {household_id}\n")
    items = await fetch_devices(household_id, product_id=product_id)
    if not items:
        typer.echo("No devices found.")
        return []
    print_table(
        [
            [
                idx,
                d.id,
                d.name,
                getattr(d.product_id, "name", getattr(d.product_id, "value", d.product_id)),
            ]
            for idx, d in enumerate(items)
        ],
        headers=["Index", "ID", "Name", "ProductId"],
    )
    return items
