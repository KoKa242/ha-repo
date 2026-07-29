import logging
import voluptuous as vol

from homeassistant import config_entries

_LOGGER = logging.getLogger(__name__)

DOMAIN = "microha"

class MicroHAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MicroHA Gateway."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Prevent duplicate instances
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="MicroHA Gateway", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )
