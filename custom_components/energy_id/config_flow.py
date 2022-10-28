"""Config flow for EnergyID integration."""
import voluptuous as vol

from typing import Any, Dict, Optional

from homeassistant import config_entries

from .const import DOMAIN, CONF_RECORD, CONF_API_KEY


class EnergyIdConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    data: Optional[Dict[str, Any]] = {
        CONF_RECORD: [],
    }

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        errors: Dict[str, str] = {}

        if not user_input:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_RECORD): str,
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional("add_another"): bool,
                }),
                errors=errors,
            )

        self.data[CONF_RECORD].append({
            CONF_RECORD: user_input[CONF_RECORD],
            CONF_API_KEY: user_input[CONF_API_KEY]
        })

        if user_input.get("add_another", False):
            return await self.async_step_user()

        return self.async_create_entry(title='EnergyID', data=self.data)
