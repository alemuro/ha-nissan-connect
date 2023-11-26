from datetime import timedelta
import logging
from homeassistant.util import Throttle
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.const import (
  UnitOfLength
)
from .const import (
    BRAND,
    CONF_VEHICLES,
    DOMAIN,
)
from .utils import build_device_info
from .entity import NissanConnectEntity

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

_LOGGER = logging.getLogger(__name__)

sensors = [
    {
        "id": "totalMileage",
        "name": "Total Mileage",
        "icon": "mdi:counter",
        "unit": UnitOfLength.KILOMETERS,
    },
    {
        "id": "fuelAutonomy",
        "name": "Fuel Autonomy",
        "icon": "mdi:gas-station",
        "unit": UnitOfLength.KILOMETERS,
    },
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Nissan Connect sensor from a config entry."""
    entities = []

    vehicles = hass.data[DOMAIN][config_entry.entry_id][CONF_VEHICLES]

    for vehicle in vehicles["data"]:
        nissan_connect_data = hass.data[DOMAIN][config_entry.entry_id]
        for sensor in sensors:
            sensor_entity = NissanConnectSensor(
                hass, nissan_connect_data, vehicle["vin"], vehicle["modelName"], sensor
            )
            entities.append(sensor_entity)

    async_add_entities(entities, update_before_add=True)

class NissanConnectSensor(SensorEntity, NissanConnectEntity):
    def __init__(
        self,
        hass: HomeAssistant,
        nissan_connect_data: dict,
        sn: str,
        model: str,
        sensor: dict,
    ):
        self._hass = hass
        self._nissan_connect_data = nissan_connect_data
        self._ncc = nissan_connect_data["controller"]
        self._model = model
        self._unit_of_measurement = sensor['unit']
        self._name = f"{self._model} {sensor['name']}"
        self._icon = sensor['icon']
        self._sn = sn
        self._state = None
        self._attribute_id = sensor['id']
        self._unique_id = f"{self._sn}_{sensor['id']}"
        NissanConnectEntity.__init__(self, nissan_connect_data, model, sn)
        SensorEntity.__init__(self)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement
    
    @property
    def native_value(self):
        return self._state

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return self._icon

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the status."""
        try:
            cockpit_status = self._ncc.get_cockpit(self._sn)
            self._state = cockpit_status["data"]["attributes"][self._attribute_id]

        except HTTPError:
            _LOGGER.error("Unable to fetch data from API")
