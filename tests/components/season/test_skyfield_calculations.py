"""Tests for Skyfield-backed season calculations."""

from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import logging

import pytest

from homeassistant.components.season import sensor
from homeassistant.components.season.const import (
    EQUATOR,
    NORTHERN,
    SOUTHERN,
    STATE_AUTUMN,
    STATE_SPRING,
    STATE_SUMMER,
    STATE_WINTER,
    TYPE_ASTRONOMICAL,
    TYPE_METEOROLOGICAL,
)


class DummyTime:
    """Simple stand-in for a Skyfield Time object."""

    def __init__(self, dt: datetime) -> None:
        """Initialize with a datetime."""
        self._dt = dt

    def utc_datetime(self) -> datetime:
        """Return the underlying datetime."""
        return self._dt


def test_calculate_astronomical_starts_returns_utc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure Skyfield season start datetimes are UTC-aware."""
    sensor._load_timescale.cache_clear()
    sensor._load_ephemeris.cache_clear()

    seasons_func = object()
    mock_ts = SimpleNamespace(utc=MagicMock(side_effect=["t0", "t1"]))
    mock_eph = object()
    mock_seasons = MagicMock(return_value=seasons_func)
    mock_find = MagicMock(
        return_value=(
            [
                DummyTime(datetime(2023, 3, 20, 21, 24)),
                DummyTime(datetime(2023, 6, 21, 14, 58, tzinfo=UTC)),
                DummyTime(datetime(2023, 9, 23, 6, 50, tzinfo=UTC)),
                DummyTime(datetime(2023, 12, 21, 3, 27, tzinfo=UTC)),
            ],
            [0, 1, 2, 3],
        )
    )

    monkeypatch.setattr(
        sensor, "_load_timescale", MagicMock(return_value=mock_ts)
    )
    monkeypatch.setattr(
        sensor, "_load_ephemeris", MagicMock(return_value=mock_eph)
    )
    monkeypatch.setattr(sensor.almanac, "seasons", mock_seasons)
    monkeypatch.setattr(sensor.almanac, "find_discrete", mock_find)

    spring, summer, autumn, winter = sensor._calculate_astronomical_starts(2023)

    mock_ts.utc.assert_has_calls(
        [((2023, 1, 1),), ((2024, 1, 1),)], any_order=False
    )
    mock_seasons.assert_called_once_with(mock_eph)
    assert mock_find.call_args[0][2] is seasons_func

    assert spring == datetime(2023, 3, 20, 21, 24, tzinfo=UTC)
    assert summer == datetime(2023, 6, 21, 14, 58, tzinfo=UTC)
    assert autumn == datetime(2023, 9, 23, 6, 50, tzinfo=UTC)
    assert winter == datetime(2023, 12, 21, 3, 27, tzinfo=UTC)


def test_get_season_falls_back_on_calculation_error(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify we fall back to fixed UTC-aware constants and warn on failure."""
    caplog.set_level(logging.WARNING)
    monkeypatch.setattr(
        sensor,
        "_calculate_astronomical_starts",
        MagicMock(side_effect=RuntimeError("boom")),
    )

    season = sensor.get_season(
        datetime(2023, 3, 21, tzinfo=UTC), NORTHERN, TYPE_ASTRONOMICAL
    )

    assert season == STATE_SPRING
    assert "Falling back to fixed astronomical season start dates" in caplog.text


def test_load_timescale_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the Skyfield timescale loader caches its result."""
    sensor._load_timescale.cache_clear()
    call_count = 0

    def fake_timescale() -> str:
        nonlocal call_count
        call_count += 1
        return f"ts{call_count}"

    monkeypatch.setattr(sensor.load, "timescale", fake_timescale)

    first = sensor._load_timescale()
    second = sensor._load_timescale()

    assert first == "ts1"
    assert first is second
    assert call_count == 1


def test_load_ephemeris_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the Skyfield ephemeris loader caches the DE430 kernel."""
    sensor._load_ephemeris.cache_clear()
    call_count = 0

    def fake_load(filename: str) -> str:
        nonlocal call_count
        call_count += 1
        assert filename == "de430.bsp"
        return f"kernel{call_count}"

    monkeypatch.setattr(sensor, "load", fake_load)

    first = sensor._load_ephemeris()
    second = sensor._load_ephemeris()

    assert first == "kernel1"
    assert first is second
    assert call_count == 1


