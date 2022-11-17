from homeassistant.helpers.entity import Entity, EntityCategory, DeviceInfo

from .energy_id.record import EnergyIDRecord

from .const import DOMAIN


class EnergyIDRecordDiagnosticEntity(Entity):
    def __init__(
            self,
            record: EnergyIDRecord,
            name: str,
            attribute: str,
            value,
            icon: str = None,
    ):
        """Initialize the entity"""
        self._record = record
        self._name = name
        self._attribute = attribute
        self._value = value
        self._icon = icon

    @property
    def unique_id(self) -> str:
        return f'{DOMAIN}-{self._record.record_id}-{self._attribute}'

    @property
    def name(self) -> str:
        return f'{self._record.display_name} - {self._name}'

    @property
    def state(self):
        return self._value

    @property
    def device_info(self) -> DeviceInfo:
        return self._record.device_info

    @property
    def entity_category(self) -> str:
        return EntityCategory.DIAGNOSTIC

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def icon(self) -> str:
        return self._icon
