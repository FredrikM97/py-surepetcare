import logging

from surepcio.security.redact import RedactSensitiveFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.addFilter(RedactSensitiveFilter())
