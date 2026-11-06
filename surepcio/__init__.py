import logging

from surepcio.client import SurePetcareClient  # noqa: F401
from surepcio.devices import get_device_features  # noqa: F401
from surepcio.household import Household, HouseholdState  # noqa: F401
from surepcio.security.redact import RedactSensitiveFilter
from surepcio.timeline import (  # noqa: F401
    MovementResource,
    TimelineEvent,
    build_event_payload,
)

f = RedactSensitiveFilter()

for name in logging.Logger.manager.loggerDict:
    if name.startswith("surepcio"):
        logging.getLogger(name).addFilter(f)
