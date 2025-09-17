from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.core import callback
from homeassistant.const import UnitOfPower

from .energy_id.meter import EnergyIDMeter
from .energy_id.record import EnergyIDRecord

import logging

_LOGGER = logging.getLogger(__name__)


def fix_datetime_offset(match):
    return f'+{match.group(1)}{match.group(2)}'


class EnergyIDRecordPeakPowerPower(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            record: EnergyIDRecord,
            meter: EnergyIDMeter,
    ):
        super().__init__(coordinator)
        self._record = record
        self._meter = meter
        self._value = None
        self._native_unit_of_measurement = UnitOfPower.KILO_WATT

    @property
    def device_info(self) -> DeviceInfo | None:
        return self._meter.device_info

    @property
    def native_value(self) -> float | None:
        return self._value

    @property
    def native_unit_of_measurement(self) -> str:
        return self._native_unit_of_measurement

    def _get_data_for_month(self, data, month_to_fetch: int):
        for serie_data in data['peaks']['data']:
            month = datetime.strptime(
                re.sub(
                    '\\+([0-2][0-9]):([0-9]{2})$',
                    fix_datetime_offset,
                    serie_data['timestamp']
                ),
                '%Y-%m-%dT%H:%M:%S%z'
            )

            if month.month == month_to_fetch:
                return serie_data['total']


class EnergyIDRecordCurrentMonthPeakPowerPower(EnergyIDRecordPeakPowerPower):
    @property
    def name(self):
        return f'{self._record.display_name}: {self._meter.display_name} - Current month PeakPower Power'

    @property
    def unique_id(self) -> str:
        return f'meter-{self._meter.meter_id}-current-month-peak-power-power'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data

        if data is not None:
            self._native_unit_of_measurement = data['peaks']['unit']
            self._value = self._get_data_for_month(data, datetime.now().month)

            self.async_write_ha_state()


class EnergyIDRecordLastMonthPeakPowerPower(EnergyIDRecordPeakPowerPower):
    @property
    def name(self):
        return f'{self._record.display_name}: {self._meter.display_name} - Last month PeakPower Power'

    @property
    def unique_id(self) -> str:
        return f'meter-{self._meter.meter_id}-last-month-peak-power-power'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data

        if data is not None:
            self._native_unit_of_measurement = data['peaks']['unit']

            first_day_of_previous_month = datetime.now().replace(day=1) - relativedelta(months=1)
            value = self._get_data_for_month(data, first_day_of_previous_month.month)

            self._value = value
            self.async_write_ha_state()


class EnergyIDRecordPeakPowerDatetime(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            record: EnergyIDRecord,
            meter: EnergyIDMeter,
    ):
        super().__init__(coordinator)
        self._record = record
        self._meter = meter
        self._value = None

    @property
    def device_info(self) -> DeviceInfo | None:
        return self._meter.device_info

    @property
    def native_value(self) -> datetime | None:
        return self._value

    def _get_data_for_month(self, data, month_to_fetch: int):
        for serie_data in data['peaks']['data']:
            month = datetime.strptime(
                re.sub(
                    '\\+([0-2][0-9]):([0-9]{2})$',
                    fix_datetime_offset,
                    serie_data['timestamp']
                ),
                '%Y-%m-%dT%H:%M:%S%z'
            )

            if month.month == month_to_fetch:
                return datetime.strptime(
                        re.sub(
                            '\\+([0-2][0-9]):([0-9]{2})$',
                            fix_datetime_offset,
                            serie_data['timestamp']
                        ),
                        '%Y-%m-%dT%H:%M:%S%z'
                    )


class EnergyIDRecordCurrentMonthPeakPowerDatetime(EnergyIDRecordPeakPowerDatetime):
    @property
    def name(self):
        return f'{self._record.display_name}: {self._meter.display_name} - Current month PeakPower Datetime'

    @property
    def unique_id(self) -> str:
        return f'meter-{self._meter.meter_id}-current-month-peak-power-datetime'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data

        if data is not None:

            self._value = self._get_data_for_month(data, datetime.now().month)
            self.async_write_ha_state()


class EnergyIDRecordLastMonthPeakPowerDatetime(EnergyIDRecordPeakPowerDatetime):
    @property
    def name(self):
        return f'{self._record.display_name}: {self._meter.display_name} - Last month PeakPower Datetime'

    @property
    def unique_id(self) -> str:
        return f'meter-{self._meter.meter_id}-last-month-peak-power-datetime'

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data

        if data is not None:
            first_day_of_previous_month = datetime.now().replace(day=1) - relativedelta(months=1)
            self._value = self._get_data_for_month(data, first_day_of_previous_month.month)
            self.async_write_ha_state()
