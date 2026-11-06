from pydantic import BaseModel, ConfigDict


class ImprovedErrorMixin(BaseModel):
    """API model defaults: ignore unknown keys, omit nulls and serialize aliases."""

    model_config = ConfigDict(extra="ignore")

    def model_dump(self, *args, **kwargs):
        kwargs.setdefault("exclude_none", True)
        kwargs.setdefault("by_alias", True)
        return super().model_dump(*args, **kwargs)
