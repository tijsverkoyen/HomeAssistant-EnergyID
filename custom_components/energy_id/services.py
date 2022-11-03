from homeassistant.core import callback, HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.entity_registry import async_entries_for_device
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_RECORD, CONF_METER_IDS, CONF_ENERGY_ID_API_HOST, CONF_API_KEY

from .energy_id.api import EnergyIDApi, EnergyIDApiError

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)


def meter_id_from_device(device: DeviceEntry) -> str:
    for identifier in device.identifiers:
        if identifier[0] == DOMAIN:
            return identifier[1].replace('meter-', '')

    return None


def find_record_for_meter_id(meter_id: str, config: dict) -> dict:
    for config_entry in config.items():
        for record in config_entry[1][CONF_RECORD]:
            for config_meter_id in record[CONF_METER_IDS]:
                if meter_id == config_meter_id:
                    return record

    return None


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for EnergyID."""

    async def handle_set_meter_reading(call: ServiceCall):
        """Handle the service call."""
        _LOGGER.debug(f'Service set_meter_reading called: {call.data}')

        # get device
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(call.data['device_id'])

        if device is None:
            raise HomeAssistantError(f'Meter not found')

        meter_id = meter_id_from_device(device)
        if meter_id is None:
            raise HomeAssistantError(f'Meter not found')

        meter_record = find_record_for_meter_id(meter_id, hass.data[DOMAIN])
        if meter_record is None:
            raise HomeAssistantError(f'Meter not found')

        api = EnergyIDApi(CONF_ENERGY_ID_API_HOST, meter_record[CONF_API_KEY])

        try:
            response = await hass.async_add_executor_job(
                api.set_meter_readings,
                meter_id,
                call.data['date'],
                call.data['value'],
            )
            _LOGGER.debug(f'Service set_meter_reading response: {response}')
        except EnergyIDApiError as e:
            raise HomeAssistantError(f'Invalid response from EnergyID API: {e}')

        entity_registry = er.async_get(hass)
        entities = async_entries_for_device(entity_registry, device.id)
        await hass.services.async_call('homeassistant', 'update_entity', {'entity_id': entities[0].entity_id})

    hass.services.async_register(
        DOMAIN,
        'set_meter_reading',
        handle_set_meter_reading,
        schema=vol.All(
            vol.Schema(
                {
                    vol.Required('device_id'): str,
                    vol.Required('date'): str,
                    vol.Required('value'): vol.Coerce(float),
                }
            )
        )
    )
