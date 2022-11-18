from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntity, STATE_CLASS_TOTAL_INCREASING
from homeassistant.core import callback
from homeassistant.const import DEVICE_CLASS_ENERGY, DEVICE_CLASS_GAS, DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_HUMIDITY, \
    VOLUME_CUBIC_METERS, VOLUME_LITERS, ENERGY_WATT_HOUR, ENERGY_KILO_WATT_HOUR, MASS_KILOGRAMS, LENGTH_KILOMETERS, \
    TEMP_CELSIUS, PERCENTAGE

from .energy_id.meter import EnergyIDMeter
from .energy_id.record import EnergyIDRecord

from .const import DOMAIN, RESPONSE_ATTRIBUTE_READINGS, RESPONSE_ATTRIBUTE_VALUE, RESPONSE_ATTRIBUTE_IGNORE

import logging

_LOGGER = logging.getLogger(__name__)


class EnergyIDMeterReading(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(
            self,
            coordinator: DataUpdateCoordinator,
            meter: EnergyIDMeter,
            record: EnergyIDRecord,
            attribute: str,
    ):
        super().__init__(coordinator)
        self._meter = meter
        self._record = record
        self._attribute = attribute
        self._state = None
        self._value = None

    @property
    def name(self):
        return f'{self._record.display_name}: {self._meter.display_name} - {self._attribute} reading'

    @property
    def device_class(self) -> str:
        if self._meter.metric.lower() in ["electricityimport", "electricityexport", "finalelectricityconsumption",
                                          "districtheatingimport", "finalheatconsumption", "districtcoolingimport",
                                          "finalcoolingconsumption", "solarphotovoltaicproduction",
                                          "solarthermalproduction", "windpowerproduction",
                                          "cogenerationpowerproduction", "electricvehiclecharging"]:
            return DEVICE_CLASS_ENERGY

        if self._meter.metric.lower() in ["naturalgasimport"]:
            if self._meter.unit.lower() in ["m³"]:
                return DEVICE_CLASS_GAS
            if self._meter.unit.lower() in ["l"]:
                return 'volume'
            if self._meter.unit.lower() in ["kWh"]:
                return DEVICE_CLASS_ENERGY

        if self._meter.metric.lower() in ["pelletsstockdraw", "woodbriquettesstockdraw", "firewoodstockdraw"]:
            if self._meter.unit.lower() in ["kg"]:
                return 'weight'
            if self._meter.unit.lower() in ["m³"]:
                return 'volume'

        if self._meter.metric.lower() in ["fueloilstockdraw", "fueloilstockbuild"]:
            return 'volume'

        if self._meter.metric.lower() in ["fueloilstocklevel"]:
            if self._meter.unit.lower() in ["m³"]:
                return DEVICE_CLASS_GAS
            if self._meter.unit.lower() in ["l"]:
                return 'volume'

        if self._meter.metric.lower() in ["propanestockdraw", "butanestockdraw"]:
            if self._meter.unit.lower() in ["kg"]:
                return 'weight'
            if self._meter.unit.lower() in ["l"]:
                return 'volume'

        if self._meter.metric.lower() in ["drinkingwaterimport", "rainwaterstockdraw", "groundwaterimport"]:
            return 'water'

        if self._meter.metric.lower() in ["indoortemperature", "outdoortemperature"]:
            return DEVICE_CLASS_TEMPERATURE

        if self._meter.metric.lower() in ["relativeindoorhumidity", "relativeoutdoorhumidity"]:
            return DEVICE_CLASS_HUMIDITY

        if self._meter.metric.lower() in ["distancetravelledbycar", "distancetravelledbybike",
                                          "distancetravelledbyscooter", "distancetravelledbymotor"]:
            return 'distance'

        if self._meter.metric.lower() in ["organicwaste", "pmdwaste", "softplasticswaste", "paperandcardboardwaste",
                                          "residualwaste", "glasswaste", "electronicwaste"]:
            if self._meter.unit.lower() in ["kg"]:
                return 'weight'
            if self._meter.unit.lower() in ["l"]:
                return 'volume'

        return None

    @property
    def device_info(self) -> DeviceInfo:
        return self._meter.device_info

    @property
    def unique_id(self) -> str:
        return f'meter-{self._meter.meter_id}-{self._attribute}-reading'

    @property
    def native_unit_of_measurement(self) -> str:
        return self._meter.unit

    @property
    def unit_of_measurement(self) -> str:
        if self._meter.unit.lower() in ["wh"]:
            return ENERGY_WATT_HOUR
        if self._meter.unit.lower() in ["kwh"]:
            return ENERGY_KILO_WATT_HOUR
        if self._meter.unit.lower() in ["l"]:
            return VOLUME_LITERS
        if self._meter.unit.lower() in ["m³"]:
            return VOLUME_CUBIC_METERS
        if self._meter.unit.lower() in ["kg"]:
            return MASS_KILOGRAMS
        if self._meter.unit.lower() in ["km"]:
            return LENGTH_KILOMETERS
        if self._meter.unit.lower() in ["°c"]:
            return TEMP_CELSIUS
        if self._meter.unit.lower() in ["%"]:
            return PERCENTAGE

        return None

    @property
    def native_value(self) -> float:
        return self._value

    @property
    def state_class(self) -> str:
        return STATE_CLASS_TOTAL_INCREASING

    @property
    def state(self) -> float:
        if self._value is None:
            return None

        if self._meter.multiplier is None:
            return self._value

        return self._value * self._meter.multiplier

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        reading = self.coordinator.data[self._meter.meter_id][RESPONSE_ATTRIBUTE_READINGS][self._attribute]
        _LOGGER.debug(f'Updating meter {self._meter.meter_id} reading {self._attribute} to {reading}')

        if reading is not None and reading[RESPONSE_ATTRIBUTE_IGNORE] is False:
            self._value = reading[RESPONSE_ATTRIBUTE_VALUE]
            self.async_write_ha_state()
