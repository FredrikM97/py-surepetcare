import logging

from surepcio.security.redact import RedactSensitiveFilter
from surepcio.client import SurePetcareClient
from surepcio.household import Household

handler = logging.StreamHandler()
handler.addFilter(RedactSensitiveFilter())

logging.basicConfig(level=logging.INFO, handlers=[handler])

