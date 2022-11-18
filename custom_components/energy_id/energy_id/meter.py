from homeassistant.helpers.entity import DeviceInfo
from ..const import DOMAIN

import datetime


class EnergyIDMeter:
    def __init__(
            self,
            automatic: bool,
            display_name: str,
            exclude_from_reports: bool,
            hidden: bool,
            meter_id: str,
            meter_type: str,
            metric: str,
            multiplier: float,
            reading_type: str,
            record_id: str,
            theme: str,
            unit: str,
            integration_id: str = None,
            activated: datetime = None,
            deactivated: datetime = None,
            comments: str = None,
            confirmed: bool = None,
            installation_number: str = None,
            connection_number: str = None,
            supplier: str = None,
            renewable: bool = None,
            brand_name: str = None,
            model_name: str = None,
            peak_power: float = None,
            meter_number: str = None,
            stock_capacity: int = None,
            interval: str = None,
            qr_key: str = None,
            qr_type: str = None
    ):
        self.automatic = automatic
        self.display_name = display_name
        self.exclude_from_reports = exclude_from_reports
        self.hidden = hidden
        self.meter_id = meter_id
        self.meter_type = meter_type
        self.metric = metric
        self.multiplier = multiplier
        self.reading_type = reading_type
        self.record_id = record_id
        self.theme = theme
        self.unit = unit
        self.integration_id = integration_id
        self.activated = activated
        self.deactivated = deactivated
        self.comments = comments
        self.confirmed = confirmed
        self.installation_number = installation_number
        self.connection_number = connection_number
        self.supplier = supplier
        self.renewable = renewable
        self.brand_name = brand_name
        self.model_name = model_name
        self.peak_power = peak_power
        self.meter_number = meter_number
        self.stock_capacity = stock_capacity
        self.interval = interval
        self.qr_key = qr_key
        self.qr_type = qr_type

    @classmethod
    def from_json(cls, json):
        return cls(
            automatic=json['automatic'],
            display_name=json['displayName'],
            exclude_from_reports=json['excludeFromReports'],
            hidden=json['hidden'],
            meter_id=json['id'],
            meter_type=json['meterType'],
            metric=json['metric'],
            multiplier=json['multiplier'],
            reading_type=json['readingType'],
            record_id=json['recordId'],
            theme=json['theme'],
            unit=json['unit'],
            integration_id=json['integrationId'] if 'integrationId' in json else None,
            activated=json['activated'] if 'activated' in json else None,
            deactivated=json['deactivated'] if 'deactivated' in json else None,
            comments=json['comments'] if 'comments' in json else None,
            confirmed=json['confirmed'] if 'confirmed' in json else None,
            installation_number=json['installationNumber'] if 'installationNumber' in json else None,
            connection_number=json['connectionNumber'] if 'connectionNumber' in json else None,
            supplier=json['supplier'] if 'supplier' in json else None,
            renewable=json['renewable'] if 'renewable' in json else None,
            brand_name=json['brandName'] if 'brandName' in json else None,
            model_name=json['modelName'] if 'modelName' in json else None,
            peak_power=json['peakPower'] if 'peakPower' in json else None,
            meter_number=json['meterNumber'] if 'meterNumber' in json else None,
            stock_capacity=json['stockCapacity'] if 'stockCapacity' in json else None,
            interval=json['interval'] if 'interval' in json else None,
            qr_key=json['qrKey'] if 'qrKey' in json else None,
            qr_type=json['qrType'] if 'qrType' in json else None
        )

    @property
    def device_info(self) -> DeviceInfo:
        manufacturer = 'EnergyID'

        if self.supplier is not None:
            manufacturer = self.supplier

        if self.brand_name is not None:
            manufacturer = self.brand_name

        model = self.meter_type
        if self.model_name is not None:
            model = self.meter_type + " " + self.model_name

        return DeviceInfo(
            configuration_url=f'https://app.energyid.eu/record/{self.record_id}/meters/{self.meter_id}/properties',
            identifiers={(DOMAIN, f'meter-{self.meter_id}')},
            name=self.display_name,
            manufacturer=manufacturer,
            model=model,
            via_device=(DOMAIN, f'record-{self.record_id}')
        )
