"""Provides the ezviz DataUpdateCoordinator."""
from datetime import timedelta
import logging

from async_timeout import timeout
from pyezvizapi.client import EzvizClient
from pyezvizapi.exceptions import HTTPError, InvalidURL, PyEzvizError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EzvizDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ezviz data."""

    def __init__(self, hass: HomeAssistant, *, api: EzvizClient, api_timeout: int) -> None:
        """Initialize global Ezviz data updater."""
        self.ezviz_client = api
        self._api_timeout = api_timeout
        update_interval = timedelta(seconds=30)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    def _update_data(self) -> dict:
        """Fetch Ezviz smart plugs data."""

        plugs = {}
        # 使用pyezvizapi库的方法获取设备列表
        switches = self.ezviz_client.get_device_infos(filter_type="SWITCH")
        for device in switches['deviceInfos']:
            for entity in switches['SWITCH'][device['deviceSerial']]:
                if int(entity['type']) is int(14):
                    device['enable'] = entity['enable']

            if device["deviceSerial"].startswith("Q"):
                plugs[device['deviceSerial']] = device

        return plugs

    async def _async_update_data(self) -> dict:
        """Fetch data from Ezviz."""
        try:
            async with timeout(self._api_timeout):
                return await self.hass.async_add_executor_job(self._update_data)

        except (InvalidURL, HTTPError, PyEzvizError) as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error