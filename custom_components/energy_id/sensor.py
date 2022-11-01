"""EnergyID sensors."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_RECORD, CONF_API_KEY, CONF_ENERGY_ID_API_HOST, CONF_METER_IDS
from .meter_reading_coordinator import EnergyIDMeterReadingCoordinator
from .energy_id.api import EnergyIDApi
from .meter_reading_sensor import EnergyIDMeterReading

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Set up the EnergyID sensor."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)

    for record_config in config[CONF_RECORD]:
        api = EnergyIDApi(CONF_ENERGY_ID_API_HOST, record_config[CONF_API_KEY])

        record = await hass.async_add_executor_job(
            api.get_record,
            record_config[CONF_RECORD]
        )

        device_registry = dr.async_get(hass)
        device_registry.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            configuration_url=f'https://app.energyid.eu/record/{record.number}/facility',
            identifiers={(DOMAIN, f'record-{record.id}')},
            manufacturer='EnergyID',
            name=record.name,
            model='Record'
        )

        meters = await hass.async_add_executor_job(
            api.get_record_meters,
            record_config[CONF_RECORD]
        )

        coordinator = EnergyIDMeterReadingCoordinator(hass, api, meters)

        record_config[CONF_METER_IDS] = []
        entities = []
        for meter in meters:
            record_config[CONF_METER_IDS].append(meter.id)
            entities.append(EnergyIDMeterReading(coordinator, meter, record, 'last'))
            entities.append(EnergyIDMeterReading(coordinator, meter, record, 'previous'))

        async_add_entities(entities)

        await coordinator.async_config_entry_first_refresh()
