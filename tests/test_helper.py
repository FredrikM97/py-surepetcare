import pytest

# Assume validate_date_fields and _try_parse are imported from the correct module
from surepy.helper import validate_date_fields

class ValidateDateFieldMock:
    @validate_date_fields("from_date", "to_date")
    async def method(self, from_date=None, to_date=None):
        return True

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "from_date,to_date,should_raise",
    [
        ("2023-01-01", "2023-01-02", False),
        ("2023-01-01T12:00:00+0000", "2023-01-02T13:00:00+0000", False),
        ("2023-01-01", "2023-01-02T13:00:00+0000", False),
        ("2023/01/01", "2023-01-02", True),
        ("2023-01-01", "bad-date", True),
    ]
)
async def test_validate_date_fields(from_date, to_date, should_raise):
    dummy = ValidateDateFieldMock()
    if should_raise:
        with pytest.raises(ValueError):
            await dummy.method(from_date=from_date, to_date=to_date)
    else:
        assert await dummy.method(from_date=from_date, to_date=to_date) is True