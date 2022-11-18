from homeassistant.helpers.entity import Entity, EntityCategory, DeviceInfo

from .energy_id.record import EnergyIDRecord

from .const import DOMAIN


class EnergyIDDiagnosticEntity(Entity):
    def __init__(
            self,
            device,
            name: str,
            attribute: str,
            value,
            icon: str = None,
    ):
        """Initialize the entity"""
        self._device = device
        self._name = name
        self._attribute = attribute
        self._value = value
        self._icon = icon

    @property
    def name(self) -> str:
        return f'{self._device.display_name} - {self._name}'

    @property
    def state(self):
        return self._value

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    @property
    def entity_category(self) -> str:
        return EntityCategory.DIAGNOSTIC

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def icon(self) -> str:
        return self._icon


class EnergyIDRecordDiagnosticEntity(EnergyIDDiagnosticEntity):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.record_id}-{self._attribute}'


class EnergyIDMeterDiagnosticEntity(EnergyIDDiagnosticEntity):
    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._device.meter_id}-{self._attribute}'
