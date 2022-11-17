"""EnergyID sensors."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_RECORD, CONF_API_KEY, CONF_ENERGY_ID_API_HOST, CONF_METER_IDS
from .meter_reading_coordinator import EnergyIDMeterReadingCoordinator
from .energy_id.api import EnergyIDApi
from .meter_reading_sensor import EnergyIDMeterReading
from .record_diagnostic_entity import EnergyIDRecordDiagnosticEntity
from .energy_id.record import EnergyIDRecord

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

        async_add_entities(_entities_for_record(record))

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


def _entities_for_record(record: EnergyIDRecord) -> list:
    entities_to_add = [
        EnergyIDRecordDiagnosticEntity(record, 'Created', 'created', record.created),
        EnergyIDRecordDiagnosticEntity(record, 'Display name', 'display_name', record.display_name),
        EnergyIDRecordDiagnosticEntity(record, 'Record ID', 'record_id', record.record_id),
        EnergyIDRecordDiagnosticEntity(record, 'Owner ID', 'owner_id', record.owner_id),
        EnergyIDRecordDiagnosticEntity(record, 'Record number', 'record_number', record.record_number),
        EnergyIDRecordDiagnosticEntity(record, 'Record Type', 'record_type', record.record_type),
        EnergyIDRecordDiagnosticEntity(record, 'Timezone', 'timezone', record.time_zone, 'mdi:map-clock'),
    ]

    if record.last_submission is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Last submission', 'last_submission', record.last_submission))

    if record.address is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Address Street', 'address_street', record.address.street))
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Address Country', 'address_country', record.address.country))
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Address Postal code', 'address_postal_code',
                                           record.address.postal_code))
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Address City', 'address_city', record.address.city, 'mdi:city'))

    if record.category is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Category', 'category', record.category))

    if record.tags is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Tags', 'tags', ', '.join(record.tags), 'mdi:tag-multiple'))

    if record.dwelling_type is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Dwelling type', 'dwelling_type', record.dwelling_type))

    if record.principal_residence is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Principal residence', 'principal_residence',
                                           record.principal_residence))

    if record.occupants is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Occupants', 'occupants', record.occupants))

    if record.occupier_type is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Occupier type', 'occupier_type', record.occupier_type))

    if record.heating_on is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Heating on', 'heating_on', record.heating_on))

    if record.auxiliary_heating_on is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Auxiliary heating on', 'auxiliary_heating_on',
                                           record.auxiliary_heating_on))

    if record.cooking_on is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Cooking on', 'cooking_on', record.cooking_on))

    if record.hot_water_on is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Hot water on', 'hot_water_on', record.hot_water_on))

    if record.floor_surface is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Floor surface', 'floor_surface', record.floor_surface))

    if record.year_of_construction is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Year of construction', 'year_of_construction',
                                           record.year_of_construction))

    if record.year_of_renovation is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Year of renovation', 'year_of_renovation',
                                           record.year_of_renovation))

    if record.energy_performance is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Energy performance', 'energy_performance',
                                           record.energy_performance))

    if record.energy_rating is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Energy rating', 'energy_rating', record.energy_rating))

    if record.energy_efficiency is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Energy efficiency', 'energy_efficiency',
                                           record.energy_efficiency))

    if record.installations is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Installations', 'installations',
                                           ', '.join(record.installations)))

    if record.plan is not None:
        entities_to_add.append(EnergyIDRecordDiagnosticEntity(record, 'Plan', 'plan', record.plan))

    if record.errors is not None:
        entities_to_add.append(EnergyIDRecordDiagnosticEntity(record, 'Errors', 'errors', record.errors,
                                                              'mdi:alert'))

    if record.benchmarking_enabled is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Benchmarking enabled', 'benchmarking_enabled',
                                           record.benchmarking_enabled))

    if record.premium_features is not None:
        entities_to_add.append(
            EnergyIDRecordDiagnosticEntity(record, 'Premium features', 'premium_features',
                                           ', '.join(record.premium_features)))

    return entities_to_add
