import logging

from surepcio.client import SurePetcareClient  # noqa: F401
from surepcio.household import Household  # noqa: F401
from surepcio.security.redact import RedactSensitiveFilter

logger = logging.getLogger("surepcio")
handler = logging.StreamHandler()
handler.addFilter(RedactSensitiveFilter())
logger.addHandler(handler)
logger.propagate = True
