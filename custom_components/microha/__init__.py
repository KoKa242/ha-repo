"""MicroHA Gateway Integration."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .api_view import MicroHAView

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MicroHA component from YAML (legacy support)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MicroHA Gateway from a config entry."""
    _LOGGER.info("Initializing MicroHA Gateway HACS integration")
    
    # Register our custom HTTP View
    hass.http.register_view(MicroHAView(hass))
    
    _LOGGER.info("MicroHA Gateway API is available at /api/microha")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
