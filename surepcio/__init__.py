import logging

from surepcio.client import SurePetcareClient  # noqa: F401
from surepcio.household import Household  # noqa: F401
from surepcio.security.redact import RedactSensitiveFilter
from surepcio.timeline import MovementResource, TimelineEvent  # noqa: F401

f = RedactSensitiveFilter()

for name in logging.Logger.manager.loggerDict:
    if name.startswith("surepcio"):
        logging.getLogger(name).addFilter(f)
