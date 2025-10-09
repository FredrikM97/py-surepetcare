from pydantic import BaseModel
from pydantic import ConfigDict


class ImprovedErrorMixin(BaseModel):
    """A mixin class to improve error handling and serialization in Pydantic models."""

    model_config = ConfigDict(extra="ignore")

    def model_dump(self, *args, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("by_alias", True)
        return super().model_dump(*args, **kwargs)
