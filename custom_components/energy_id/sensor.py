"""EnergyID sensors."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_RECORD, CONF_API_KEY, CONF_ENERGY_ID_API_HOST, CONF_METER_IDS
from .energy_id.api import EnergyIDApi
from .energy_id.meter import EnergyIDMeter
from .energy_id.record import EnergyIDRecord
from .diagnostic_entity import EnergyIDRecordDiagnosticEntity, EnergyIDMeterDiagnosticEntity
from .meter_reading_coordinator import EnergyIDMeterReadingCoordinator
from .meter_reading_sensor import EnergyIDMeterReading
from .peak_power_coordinator import EnergyIDRecordPeakPowerCoordinator
from .peak_power_sensor import EnergyIDRecordCurrentMonthPeakPowerPower, \
    EnergyIDRecordCurrentMonthPeakPowerDatetime, EnergyIDRecordLastMonthPeakPowerPower, \
    EnergyIDRecordLastMonthPeakPowerDatetime

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

        entities = _entities_for_record(record)
        async_add_entities(entities)

        meters = await hass.async_add_executor_job(
            api.get_record_meters,
            record_config[CONF_RECORD]
        )

        meter_reading_coordinator = EnergyIDMeterReadingCoordinator(hass, api, meters)

        if record.plan == "premium" or record.plan == "premiumHr":
            record_peak_power_coordinator = EnergyIDRecordPeakPowerCoordinator(hass, api, record)

        record_config[CONF_METER_IDS] = []
        entities = []
        for meter in meters:
            record_config[CONF_METER_IDS].append(meter.meter_id)
            async_add_entities(_entities_for_meter(meter))
            entities.append(EnergyIDMeterReading(meter_reading_coordinator, meter, record, 'last'))
            entities.append(EnergyIDMeterReading(meter_reading_coordinator, meter, record, 'previous'))

            if record.plan == "premium" or record.plan == "premiumHr":
                if meter.meter_type == 'electricity' and meter.metric == 'gridImportActivePower':
                    entities.append(
                        EnergyIDRecordCurrentMonthPeakPowerPower(record_peak_power_coordinator, record, meter))
                    entities.append(
                        EnergyIDRecordCurrentMonthPeakPowerDatetime(record_peak_power_coordinator, record, meter))
                    entities.append(EnergyIDRecordLastMonthPeakPowerPower(record_peak_power_coordinator, record, meter))
                    entities.append(
                        EnergyIDRecordLastMonthPeakPowerDatetime(record_peak_power_coordinator, record, meter))

        async_add_entities(entities)

        await meter_reading_coordinator.async_config_entry_first_refresh()

        if record.plan == "premium" or record.plan == "premiumHr":
            await record_peak_power_coordinator.async_config_entry_first_refresh()


def _entities_for_record(record: EnergyIDRecord) -> list:
    entities_to_add = [
        EnergyIDRecordDiagnosticEntity(record, 'Created', 'created', record.created),
        EnergyIDRecordDiagnosticEntity(record, 'Display name', 'display_name', record.display_name),
        EnergyIDRecordDiagnosticEntity(record, 'Record ID', 'record_id', record.record_id),
        EnergyIDRecordDiagnosticEntity(record, 'Owner ID', 'owner_id', record.owner_id),
        EnergyIDRecordDiagnosticEntity(record, 'Record number', 'record_number', record.record_number),
        EnergyIDRecordDiagnosticEntity(record, 'Record type', 'record_type', record.record_type),
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


def _entities_for_meter(meter: EnergyIDMeter) -> list:
    entities_to_add = [
        EnergyIDMeterDiagnosticEntity(meter, 'Automatic', 'automatic', meter.automatic),
        EnergyIDMeterDiagnosticEntity(meter, 'Display name', 'display_name', meter.display_name),
        EnergyIDMeterDiagnosticEntity(meter, 'Exclude from reports', 'exclude_from_reports', meter.exclude_from_reports),
        EnergyIDMeterDiagnosticEntity(meter, 'Hidden', 'hidden', meter.hidden),
        EnergyIDMeterDiagnosticEntity(meter, 'Meter ID', 'meter_id', meter.meter_id),
        EnergyIDMeterDiagnosticEntity(meter, 'Meter type', 'meter_type', meter.meter_type),
        EnergyIDMeterDiagnosticEntity(meter, 'Metric', 'metric', meter.metric),
        EnergyIDMeterDiagnosticEntity(meter, 'Multiplier', 'multiplier', meter.multiplier),
        EnergyIDMeterDiagnosticEntity(meter, 'Reading type', 'reading_type', meter.reading_type),
        EnergyIDMeterDiagnosticEntity(meter, 'Record ID', 'record_id', meter.record_id),
        EnergyIDMeterDiagnosticEntity(meter, 'Theme', 'theme', meter.theme),
        EnergyIDMeterDiagnosticEntity(meter, 'Unit', 'unit', meter.unit),
    ]

    if meter.integration_id is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Integration ID', 'integration_id', meter.integration_id))
    if meter.activated is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Activated', 'activated', meter.activated))
    if meter.deactivated is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Deactivated', 'deactivated', meter.deactivated))
    if meter.comments is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Comments', 'comments', meter.comments))
    if meter.confirmed is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Confirmed', 'confirmed', meter.confirmed))
    if meter.installation_number is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Installation number', 'installation_number', meter.installation_number))
    if meter.connection_number is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Connection number', 'connection_number', meter.connection_number))
    if meter.supplier is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Supplier', 'supplier', meter.supplier))
    if meter.renewable is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Renewable', 'renewable', meter.renewable))
    if meter.brand_name is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Brand name', 'brand_name', meter.brand_name))
    if meter.model_name is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Model name', 'model_name', meter.model_name))
    if meter.peak_power is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Peak power', 'peak_power', meter.peak_power))
    if meter.meter_number is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Meter number', 'meter_number', meter.meter_number))
    if meter.stock_capacity is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Stock capacity', 'stock_capacity', meter.stock_capacity))
    if meter.interval is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'Interval', 'interval', meter.interval))
    if meter.qr_key is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'QR key', 'qr_key', meter.qr_key))
    if meter.qr_type is not None:
        entities_to_add.append(
            EnergyIDMeterDiagnosticEntity(meter, 'QR type', 'qr_type', meter.qr_type))

    return entities_to_add
