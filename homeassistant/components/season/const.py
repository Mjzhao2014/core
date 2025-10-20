"""Constants for the Season integration."""

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "season"
PLATFORMS: Final = [Platform.SENSOR]

DEFAULT_NAME: Final = "Season"

TYPE_ASTRONOMICAL: Final = "astronomical"
TYPE_METEOROLOGICAL: Final = "meteorological"

VALID_TYPES: Final = [TYPE_ASTRONOMICAL, TYPE_METEOROLOGICAL]

# Hemisphere and season string constants used by the season sensor.
EQUATOR: Final = "equator"
NORTHERN: Final = "northern"
SOUTHERN: Final = "southern"

STATE_AUTUMN: Final = "autumn"
STATE_SPRING: Final = "spring"
STATE_SUMMER: Final = "summer"
STATE_WINTER: Final = "winter"

# Map a Northern Hemisphere season to its Southern Hemisphere opposite.
HEMISPHERE_SEASON_SWAP: Final = {
    STATE_WINTER: STATE_SUMMER,
    STATE_SPRING: STATE_AUTUMN,
    STATE_AUTUMN: STATE_SPRING,
    STATE_SUMMER: STATE_WINTER,
}
