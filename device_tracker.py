"""Support for UPC ConnectBox router."""
from __future__ import annotations

import logging

from connect_box import ConnectBox
from connect_box.exceptions import ConnectBoxError, ConnectBoxLoginError
import voluptuous as vol

from homeassistant.components.device_tracker import (
    DOMAIN,
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    DeviceScanner,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

CONF_LEGACY_MODE = "legacy_mode"
CONF_ENCRYPT_PASSWORD = "encrypt_password"

DEFAULT_IP = "192.168.0.1"
DEFAULT_USERNAME = "admin"
DEFAULT_LEGACY_MODE = True
DEFAULT_ENCRYPT_PASSWORD = True

PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_IP): cv.string,
        vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
        vol.Optional(CONF_LEGACY_MODE, default=DEFAULT_LEGACY_MODE): cv.boolean,
        vol.Optional(CONF_ENCRYPT_PASSWORD, default=DEFAULT_ENCRYPT_PASSWORD): cv.boolean,
    }
)


async def async_get_scanner(
    hass: HomeAssistant, config: ConfigType
) -> UPCDeviceScanner | None:
    """Return the UPC device scanner."""
    conf = config[DOMAIN]
    session = async_get_clientsession(hass)
    connect_box = ConnectBox(
        session,
        conf[CONF_PASSWORD],
        host=conf[CONF_HOST],
        username=conf[CONF_USERNAME],
        use_token=conf[CONF_LEGACY_MODE],
        encrypt_password=conf[CONF_ENCRYPT_PASSWORD],
    )

    # Check login data
    try:
        await connect_box.async_initialize_token()
    except ConnectBoxLoginError as err:
        _LOGGER.error("ConnectBox login data error! %s", err)
        return None
    except ConnectBoxError as err:
        _LOGGER.error("ConnectBox login error! %s", err)
        pass

    async def _shutdown(event):
        """Shutdown event."""
        await connect_box.async_close_session()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _shutdown)

    return UPCDeviceScanner(connect_box)


class UPCDeviceScanner(DeviceScanner):
    """Class which queries a router running UPC ConnectBox firmware."""

    def __init__(self, connect_box: ConnectBox) -> None:
        """Initialize the scanner."""
        self.connect_box: ConnectBox = connect_box

    async def async_scan_devices(self) -> list[str]:
        """Scan for new devices and return a list with found device IDs."""
        try:
            await self.connect_box.async_get_devices()
        except ConnectBoxError:
            return []

        return [device.mac for device in self.connect_box.devices]

    async def async_get_device_name(self, device: str) -> str | None:
        """Get the device name (the name of the wireless device not used)."""
        for connected_device in self.connect_box.devices:
            if (
                connected_device.mac == device
                and connected_device.hostname.lower() != "unknown"
            ):
                return connected_device.hostname

        return None
