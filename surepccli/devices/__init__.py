from .dual_scan_connect import dualscanconnect
from .feeder_connect import feederconnect
from .hub import hub as hb
from .pet_door import petdoor


def device_subgroups():
    """Return all device Typer subgroups (for wiring)."""
    return [feederconnect, dualscanconnect, petdoor, hb]
