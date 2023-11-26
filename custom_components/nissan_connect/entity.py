import logging
from homeassistant.helpers.entity import DeviceInfo, Entity
from .const import (
    BRAND,
)
from .utils import build_device_info

_LOGGER = logging.getLogger(__name__)

class NissanConnectEntity(Entity):
    def __init__(
        self,
        nissan_connect_data: dict,
        model: str,
        sn: str,
    ):
        self._enabled = False
        self._model = model
        self._nissan_connect_data = nissan_connect_data
        self._ncc = nissan_connect_data["controller"]
        self._sn = sn

    @property
    def device_info(self) -> DeviceInfo:
        return build_device_info(self._model, self._sn)

    @property
    def model(self):
        return self._model

    @property
    def brand(self):
        return BRAND

    async def async_added_to_hass(self) -> None:
        self._enabled = True

    async def async_will_remove_from_hass(self) -> None:
        self._enabled = False

