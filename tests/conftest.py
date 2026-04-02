# tests/conftest.py
"""
Shared pytest fixtures.

Provides a mock I2CBus that records all calls without touching real hardware.
This lets the test suite run on any OS, including Windows.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from raspbot.bus import I2CBus


@pytest.fixture()
def mock_bus() -> MagicMock:
    """Return a MagicMock that mimics I2CBus without opening a real I2C device."""
    bus = MagicMock(spec=I2CBus)
    bus.read_block_data.return_value = [0]
    return bus
