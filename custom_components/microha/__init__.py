import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

from .api_view import MicroHAView

_LOGGER = logging.getLogger(__name__)

DOMAIN = "microha"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the MicroHA Gateway integration from configuration.yaml."""
    _LOGGER.info("Initializing MicroHA Gateway HACS integration")
    
    # Register our custom HTTP View
    hass.http.register_view(MicroHAView(hass))
    
    _LOGGER.info("MicroHA Gateway API is available at /api/microha")
    return True
