from homeassistant.helpers.entity import DeviceInfo

from .const import (
    BRAND,
    DOMAIN,
)

def build_device_info(model, sn) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, sn)},
        name=f"{BRAND} {model}",
        manufacturer=BRAND,
        model=model,
        sw_version="Not provided",
    )