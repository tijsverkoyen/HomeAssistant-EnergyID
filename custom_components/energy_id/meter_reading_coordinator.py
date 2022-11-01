from datetime import timedelta, datetime
from typing import List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .energy_id.api import EnergyIDApi
from .energy_id.meter import EnergyIDMeter

from .const import DOMAIN, RESPONSE_ATTRIBUTE_READINGS

import re
import logging

_LOGGER = logging.getLogger(__name__)


class EnergyIDMeterReadingCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: EnergyIDApi, meters: List[EnergyIDMeter]):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="EnergyIDMeterReadingCoordinator",
            update_interval=timedelta(minutes=15),
        )
        self.api = api
        self.meters = meters

    async def _async_update_data(self):
        def fix_datetime_offset(match):
            return f'+{match.group(1)}{match.group(2)}'

        data = {}

        for meter in self.meters:
            response = await self.hass.async_add_executor_job(
                self.api.get_meter_readings,
                meter.id,
                2
            )

            data[meter.id] = {}
            reading_data = {
                'last': None,
                'previous': None,
            }
            last_timestamp = None

            for reading in response[RESPONSE_ATTRIBUTE_READINGS]:
                timestamp = datetime.strptime(
                    re.sub(
                        '\+([0-2][0-9]):([0-9]{2})$',
                        fix_datetime_offset,
                        reading['timestamp']
                    ),
                    '%Y-%m-%dT%H:%M:%S%z'
                )

                if last_timestamp is None:
                    reading_data['last'] = reading
                    reading_data['previous'] = reading
                elif last_timestamp < timestamp:
                    reading_data['last'] = reading
                elif last_timestamp > timestamp:
                    reading_data['previous'] = reading

                last_timestamp = timestamp

            data[meter.id][RESPONSE_ATTRIBUTE_READINGS] = reading_data

        return data
