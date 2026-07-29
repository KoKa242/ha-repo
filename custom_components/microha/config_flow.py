import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MicroHAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MicroHA Gateway."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Check if already configured
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # We don't really need any config data, just register the entry
            return self.async_create_entry(title="MicroHA Gateway", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )
