"""Fixtures for Season integration tests."""

from __future__ import annotations

iiiimport asyncio
from collections.abc import Generator
from unittest.mock import patch

import pytest

from homeassistant.components.season.const import DOMAIN, TYPE_ASTRONOMICAL
from homeassistant.const import CONF_TYPE

from tests.common import MockConfigEntry


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        title="Season",
        domain=DOMAIN,
        data={CONF_TYPE: TYPE_ASTRONOMICAL},
        unique_id=TYPE_ASTRONOMICAL,
    )


@pytest.fixture
def mock_setup_entry() -> Generator[None]:
    """Mock setting up a config entry."""
    with patch("homeassistant.components.season.async_setup_entry", return_value=True):
        yield
