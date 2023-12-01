from datetime import timedelta
import logging
from homeassistant.util import Throttle
from homeassistant.core import HomeAssistant
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.const import (
  UnitOfLength
)
from .const import (
    BRAND,
    CONF_VEHICLES,
    DOMAIN,
)

from .entity import NissanConnectEntity
from .utils import build_device_info

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Nissan Connect sensor from a config entry."""
    entities = []

    vehicles = hass.data[DOMAIN][config_entry.entry_id][CONF_VEHICLES]

    for vehicle in vehicles["data"]:
        nissan_connect_data = hass.data[DOMAIN][config_entry.entry_id]
        sensor_entity = NissanConnectTracker(
            hass, nissan_connect_data, vehicle["vin"], vehicle["modelName"]
        )
        entities.append(sensor_entity)

    async_add_entities(entities, update_before_add=True)

class NissanConnectTracker(TrackerEntity, NissanConnectEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        nissan_connect_data: dict,
        sn: str,
        model: str,
    ):
        self._hass = hass
        self._nissan_connect_data = nissan_connect_data
        self._ncc = nissan_connect_data["controller"]
        self._model = model
        self._name = f"{self._model} location"
        self._icon = "mdi:car"
        self._sn = sn
        self._latitude = None
        self._longitude = None
        self._unique_id = f"{self._sn}_location"
        NissanConnectEntity.__init__(self, nissan_connect_data, model, sn)
        TrackerEntity.__init__(self)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return self._icon

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self._latitude

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self._longitude

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def location_accuracy(self) -> int:
        """Return the location accuracy of the device.

        Value in meters.
        """
        return 0

    @property
    def should_poll(self):
        """No polling needed."""
        return True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the status."""
        self._ncc.refresh_data()
        location = self._ncc.get_location(self._sn)
        self._latitude = location["attributes"]["gpsLatitude"]
        self._longitude = location["attributes"]["gpsLongitude"]
