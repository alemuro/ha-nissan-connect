"""Config flow for Nissan Connect."""
import logging

from requests.models import HTTPError
from .NissanConnect import NissanConnectClient
import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_VEHICLES,
    CONF_USERNAME,
    CONF_PASSWORD,
    DOMAIN,
    STEP_LOGIN,
)

_LOGGER = logging.getLogger(__name__)


class NissanConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Nissan Connect config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Init."""
        pass

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return await self.async_step_login()

    async def async_step_login(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            try:
                # Validate credentials
                ncc = NissanConnectClient(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
                vehicles = await self.hass.async_add_executor_job(ncc.get_vehicles)

                # Create devices
                return self.async_create_entry(
                    title="Nissan Connect",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_VEHICLES: vehicles,
                    },
                )

            except:
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id=STEP_LOGIN,
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )