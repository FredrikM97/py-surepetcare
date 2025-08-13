from typing import get_type_hints
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import model_validator

from surepetcare.security.exceptions import ValidationMissingFieldsError


class ImprovedErrorMixin(BaseModel):
    @model_validator(mode="after")
    def check_required_fields(cls, values):
        missing = []
        hints = get_type_hints(cls)
        for field, hint in hints.items():
            is_optional = getattr(hint, "__origin__", None) is Optional or (
                hasattr(hint, "__args__") and type(None) in getattr(hint, "__args__", [])
            )
            has_default = getattr(cls, field, None) is not None
            if not is_optional and not has_default and getattr(values, field, None) is None:
                missing.append(field)
        if missing:
            raise ValidationMissingFieldsError(
                f"Missing required fields for {cls.__name__}: {missing}. "
                f"Input was: {values.dict() if hasattr(values, 'dict') else values}"
            )
        return values

    model_config = ConfigDict(extra="ignore")
