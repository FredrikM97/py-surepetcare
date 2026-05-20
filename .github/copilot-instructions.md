# Copilot Instructions

## Testing Conventions

### Use fixtures over boilerplate
Shared setup (client creation, mock registration, API calls) belongs in a `conftest.py` fixture, not repeated in every test.
Tests should receive ready-to-use objects via fixtures and focus only on the assertion logic.

### Use real objects instead of mocks
Prefer constructing real `Pet`, device, and `Household` objects fetched via the API over `MagicMock`.
Use `@pytest.mark.parametrize("device_names", [...])` with `mock_devices` and `register_device_api_mocks` to load fixtures and instantiate real objects via the actual API client.

### Consolidate related tests
Merge closely related edge cases into a single test function rather than one function per case.
Only split tests when they cover genuinely different behaviours that would be confusing to combine.

### `aresponses` only when needed
Only request `aresponses` as a fixture parameter when the test makes raw `aresponses.add(...)` calls that can't go through the helper fixture.
Use the `add_api_json_response` fixture instead of the bare `aresponses` server for registering JSON responses — it is pre-bound and requires no `aresponses` argument:

```python
async def test_something(add_api_json_response):
    add_api_json_response("GET", "/some/path", {"key": "value"}, status=200)
```

Tests that only inspect already-fetched objects need neither `aresponses` nor `add_api_json_response`.

### Always annotate local variables with types
Every variable assigned from an API call or fixture must carry an explicit type annotation so the intent is immediately clear:

For async API tests, register mocks, then fetch objects inside the client context, then assert outside:

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("device_names", [["pet", "feeder_connect", "household"]])
async def test_something(register_device_api_mocks, mock_devices):
    register_device_api_mocks(mock_devices)
    async with SurePetcareClient() as client:
        household: Household = await client.api(Household.get_household(7777))
        pets: list[Pet] = await client.api(household.get_pets())
        devices: list[FeederConnect] = await client.api(household.get_devices())

    # assertions outside the client block
    commands: list[Command] = household.fetch_pet_device_assignments()
    assert ...
```

### Remove unused imports and dead code
Delete any import, helper function, or variable that is no longer referenced after a change.
Do not leave orphaned imports or stubs behind.
