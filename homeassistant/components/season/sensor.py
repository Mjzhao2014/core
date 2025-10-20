"""Support for Season sensors."""

from __future__ import annotations

from datetime import UTC, date, datetime
from functools import lru_cache
import logging
from typing import TYPE_CHECKING

from skyfield import almanac
from skyfield.api import load

if TYPE_CHECKING:
    from skyfield.jpllib import SpiceKernel
    from skyfield.timelib import Timescale

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

LOGGER = logging.getLogger(__name__)


# The Skyfield ephemeris and timescale objects are cached, both to avoid
# repeated network requests to download de430 and to amortize the cost of
# building them over all season calculations.

@lru_cache(maxsize=1)
def _load_timescale() -> Timescale:
    """Return a cached Skyfield Timescale for UTC calculations."""
    return load.timescale()


@lru_cache(maxsize=1)
def _load_ephemeris() -> SpiceKernel:
    """Return a cached JPL DE430 ephemeris if available."""
    return load("de430.bsp")


def _calculate_astronomical_starts(
    year: int,
) -> tuple[datetime, datetime, datetime, datetime]:
    """Return UTC-aware start datetimes of seasons for the given year using Skyfield.

    Constructs Skyfield Time values from a Timescale instance and returns
    UTC-aware datetime objects for each season start.
    """
    ts = _load_timescale()
    eph = _load_ephemeris()
    # Construct Skyfield Time values from the Timescale for the year range
    t0 = ts.utc(year, 1, 1)
    t1 = ts.utc(year + 1, 1, 1)
    times, events = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    # Map event code to the UTC-aware datetime; 0=March equinox, 1=June solstice,
    # 2=September equinox, 3=December solstice.
    event_map: dict[int, datetime] = {}
    for event_code, t in zip(events, times):
        # Convert Skyfield Time to UTC-aware datetime
        utc_dt = t.utc_datetime()
        # Ensure it's UTC-aware (Skyfield should already provide this, but be explicit)
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=UTC)
        event_map[event_code] = utc_dt
    return (
        event_map[0],
        event_map[1],
        event_map[2],
        event_map[3],
    )


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


def get_season(
    current_date: date, hemisphere: str, season_tracking_type: str
) -> str | None:
    """Calculate the current season at the given date and hemisphere.

    All datetime comparisons use UTC-aware datetime objects.
    """
    if hemisphere == EQUATOR:
        return None

    # Ensure current_date is a UTC-aware datetime for comparisons
    if isinstance(current_date, datetime):
        if current_date.tzinfo is None:
            current_date = current_date.replace(tzinfo=UTC)
    else:
        # Convert date to UTC-aware datetime at midnight
        current_date = datetime.combine(current_date, datetime.min.time(), tzinfo=UTC)

    if season_tracking_type == TYPE_ASTRONOMICAL:
        try:
            spring_start, summer_start, autumn_start, winter_start = (
                _calculate_astronomical_starts(current_date.year)
            )
        except Exception as err:
            # If we cannot compute astronomical season start times, fall back
            # to approximate UTC-aware equinox and solstice dates for the given year.
            LOGGER.warning(
                "Falling back to fixed astronomical season start dates: %s", err
            )
            spring_start = datetime(current_date.year, 3, 20, tzinfo=UTC)
            summer_start = datetime(current_date.year, 6, 21, tzinfo=UTC)
            autumn_start = datetime(current_date.year, 9, 22, tzinfo=UTC)
            winter_start = datetime(current_date.year, 12, 21, tzinfo=UTC)
    else:
        # Meteorological seasons begin on the first of the month (UTC-aware).
        spring_start = datetime(current_date.year, 3, 1, tzinfo=UTC)
        summer_start = datetime(current_date.year, 6, 1, tzinfo=UTC)
        autumn_start = datetime(current_date.year, 9, 1, tzinfo=UTC)
        winter_start = datetime(current_date.year, 12, 1, tzinfo=UTC)
    season = STATE_WINTER
    if spring_start <= current_date < summer_start:
        season = STATE_SPRING
    elif summer_start <= current_date < autumn_start:
        season = STATE_SUMMER
    elif autumn_start <= current_date < winter_start:
        season = STATE_AUTUMN
    # If user is located in the southern hemisphere swap the season.
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
        """Initialize the season."""
        self._attr_unique_id = entry.entry_id
        self.hemisphere = hemisphere
        self.type = entry.data[CONF_TYPE]
        self._attr_device_info = DeviceInfo(
            name="Season",
            identifiers={(DOMAIN, entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
        )

    def update(self) -> None:
        """Update season with current UTC time."""
        self._attr_native_value = get_season(utcnow(), self.hemisphere, self.type)
