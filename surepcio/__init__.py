import logging

from surepcio.client import SurePetcareClient  # noqa: F401
from surepcio.household import Household  # noqa: F401
from surepcio.security.redact import RedactSensitiveFilter

handler = logging.StreamHandler()
handler.addFilter(RedactSensitiveFilter())

logging.basicConfig(level=logging.INFO, handlers=[handler])
