import logging

from surepcio.security.redact import RedactSensitiveFilter

handler = logging.StreamHandler()
handler.addFilter(RedactSensitiveFilter())

logging.basicConfig(level=logging.INFO, handlers=[handler])
