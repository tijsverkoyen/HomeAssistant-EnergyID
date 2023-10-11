from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .energy_id.api import EnergyIDApi
from .energy_id.record import EnergyIDRecord

from .const import RESPONSE_ATTRIBUTE_VALUE

import logging

_LOGGER = logging.getLogger(__name__)


class EnergyIDRecordPeakPowerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: EnergyIDApi, record: EnergyIDRecord):
        super().__init__(
            hass,
            _LOGGER,
            name="EnergyIDRecordPeakPowerCoordinator",
            update_interval=timedelta(hours=1),
        )
        self.api = api
        self.record = record

    async def _async_update_data(self):
        def fix_datetime_offset(match):
            return f'+{match.group(1)}{match.group(2)}'

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        first_day_of_previous_month = today.replace(day=1) - relativedelta(months=1)
        last_day_of_current_month = today + relativedelta(day=31)

        response = await self.hass.async_add_executor_job(
            self.api.get_record_analyse_peak_power,
            self.record.record_number,
            first_day_of_previous_month,
            last_day_of_current_month
        )

        if RESPONSE_ATTRIBUTE_VALUE in response:
            for value in response[RESPONSE_ATTRIBUTE_VALUE]:
                if value['id'] == f'/records/{self.record.record_id}/analyses/peakPower':
                    return value

        return None
