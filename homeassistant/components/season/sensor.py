"""Support for Season sensors."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
import logging

from skyfield.api import load
from skyfield.searchlib import find_discrete

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import utcnow

from .const import (
    DOMAIN,
    EQUATOR,
    HEMISPHERE_SEASON_SWAP,
    NORTHERN,
    SOUTHERN,
    STATE_AUTUMN,
    STATE_SPRING,
    STATE_SUMMER,
    STATE_WINTER,
    TYPE_ASTRONOMICAL,
)

_LOGGER = logging.getLogger(__name__)

# Fallback dates for when Skyfield calculations fail (UTC-aware)
# These are approximate dates for northern hemisphere astronomical seasons
FALLBACK_SPRING_START = datetime(2000, 3, 20, 7, 35, tzinfo=UTC)
FALLBACK_SUMMER_START = datetime(2000, 6, 21, 1, 48, tzinfo=UTC)
FALLBACK_AUTUMN_START = datetime(2000, 9, 22, 17, 27, tzinfo=UTC)
FALLBACK_WINTER_START = datetime(2000, 12, 21, 13, 37, tzinfo=UTC)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform from config entry."""
    hemisphere = EQUATOR
    if hass.config.latitude < 0:
        hemisphere = SOUTHERN
    elif hass.config.latitude > 0:
        hemisphere = NORTHERN

    async_add_entities([SeasonSensorEntity(entry, hemisphere)], True)


@lru_cache(maxsize=8)
def _get_timescale():
    """Get or create a Skyfield timescale object with LRU caching."""
    return load.timescale()


@lru_cache(maxsize=8)
def _get_ephemeris():
    """Get or create a Skyfield ephemeris object with LRU caching."""
    return load("de421.bsp")


def _calculate_astronomical_seasons(
    year: int,
) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Calculate astronomical season start times for a given year using Skyfield.

    Returns UTC-aware datetime objects for spring, summer, autumn, and winter starts.
    Falls back to fixed dates if calculation fails.
    """
    try:
        ts = _get_timescale()
        eph = _get_ephemeris()
        earth = eph["earth"]

        # Define the time range for the year
        start_time = ts.utc(year, 1, 1)
        end_time = ts.utc(year + 1, 1, 1)

        # Use Skyfield's seasons() function to determine season boundaries
        from skyfield import almanac

        t, y = find_discrete(start_time, end_time, almanac.seasons(eph))

        # y values: 0=spring, 1=summer, 2=autumn, 3=winter
        season_times = {}
        for time_obj, season_code in zip(t, y):
            if season_code == 0:  # Spring (Vernal Equinox)
                season_times["spring"] = time_obj.utc_datetime()
            elif season_code == 1:  # Summer (Summer Solstice)
                season_times["summer"] = time_obj.utc_datetime()
            elif season_code == 2:  # Autumn (Autumnal Equinox)
                season_times["autumn"] = time_obj.utc_datetime()
            elif season_code == 3:  # Winter (Winter Solstice)
                season_times["winter"] = time_obj.utc_datetime()

        # Ensure all season times are present
        spring_start = season_times.get(
            "spring", FALLBACK_SPRING_START.replace(year=year)
        )
        summer_start = season_times.get(
            "summer", FALLBACK_SUMMER_START.replace(year=year)
        )
        autumn_start = season_times.get(
            "autumn", FALLBACK_AUTUMN_START.replace(year=year)
        )
        winter_start = season_times.get(
            "winter", FALLBACK_WINTER_START.replace(year=year)
        )

        # Ensure all datetime objects are UTC-aware
        if spring_start.tzinfo is None:
            spring_start = spring_start.replace(tzinfo=UTC)
        if summer_start.tzinfo is None:
            summer_start = summer_start.replace(tzinfo=UTC)
        if autumn_start.tzinfo is None:
            autumn_start = autumn_start.replace(tzinfo=UTC)
        if winter_start.tzinfo is None:
            winter_start = winter_start.replace(tzinfo=UTC)

        return spring_start, summer_start, autumn_start, winter_start

    except Exception as err:
        _LOGGER.warning(
            "Failed to calculate astronomical seasons using Skyfield for year %d: %s. "
            "Using fallback dates",
            year,
            err,
        )
        # Return fallback dates with the correct year
        return (
            FALLBACK_SPRING_START.replace(year=year),
            FALLBACK_SUMMER_START.replace(year=year),
            FALLBACK_AUTUMN_START.replace(year=year),
            FALLBACK_WINTER_START.replace(year=year),
        )


def _calculate_meteorological_seasons(
    year: int,
) -> tuple[datetime, datetime, datetime, datetime]:
    """
    Calculate meteorological season start times for a given year.

    Returns UTC-aware datetime objects for spring, summer, autumn, and winter starts.
    Meteorological seasons are fixed: March 1, June 1, September 1, December 1.
    """
    spring_start = datetime(year, 3, 1, tzinfo=UTC)
    summer_start = datetime(year, 6, 1, tzinfo=UTC)
    autumn_start = datetime(year, 9, 1, tzinfo=UTC)
    winter_start = datetime(year, 12, 1, tzinfo=UTC)

    return spring_start, summer_start, autumn_start, winter_start


def get_season(
    current_date: datetime, hemisphere: str, season_tracking_type: str
) -> str | None:
    """
    Calculate the current season.

    Args:
        current_date: The current date/time (should be UTC-aware)
        hemisphere: The hemisphere ("northern", "southern", or "equator")
        season_tracking_type: "astronomical" or "meteorological"

    Returns:
        The current season name, or None for equator locations.
    """
    if hemisphere == EQUATOR:
        return None

    # Ensure current_date is UTC-aware
    if current_date.tzinfo is None:
        current_date = current_date.replace(tzinfo=UTC)

    year = current_date.year

    if season_tracking_type == TYPE_ASTRONOMICAL:
        spring_start, summer_start, autumn_start, winter_start = (
            _calculate_astronomical_seasons(year)
        )
    else:
        spring_start, summer_start, autumn_start, winter_start = (
            _calculate_meteorological_seasons(year)
        )

    # Determine the current season
    season = STATE_WINTER
    if spring_start <= current_date < summer_start:
        season = STATE_SPRING
    elif summer_start <= current_date < autumn_start:
        season = STATE_SUMMER
    elif autumn_start <= current_date < winter_start:
        season = STATE_AUTUMN

    # If user is located in the southern hemisphere, swap the season
    if hemisphere == NORTHERN:
        return season
    return HEMISPHERE_SEASON_SWAP.get(season)


class SeasonSensorEntity(SensorEntity):
    """Representation of the current season."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_has_entity_name = True
    _attr_name = None
    _attr_options = ["spring", "summer", "autumn", "winter"]
    _attr_translation_key = "season"

    def __init__(self, entry: ConfigEntry, hemisphere: str) -> None:
        """Initialize the season sensor."""
        self._attr_unique_id = entry.entry_id
        self.hemisphere = hemisphere
        self.type = entry.data[CONF_TYPE]
        self._attr_device_info = DeviceInfo(
            name="Season",
            identifiers={(DOMAIN, entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
        )

    def update(self) -> None:
        """Update the current season."""
        self._attr_native_value = get_season(utcnow(), self.hemisphere, self.type)
