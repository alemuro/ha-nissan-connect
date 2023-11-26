import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo

from .NissanConnect import NissanConnectClient
from .const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    """Set up Nissan Connect sensors based on a config entry."""
    _LOGGER.info("Setting up Nissan Connect integration")
    hass.data.setdefault(DOMAIN, {})

    ncc = NissanConnectClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])

    hass.data[DOMAIN][entry.entry_id] = {
        "controller": ncc,
        "vehicles": entry.data["vehicles"],
        "lastTimeSync": 0,
        "lastFirmwareCheck": 0,
        "latestFirmwareVersion": False,
        "entities": [],
        "name": "test",
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "device_tracker")
    )
    return True