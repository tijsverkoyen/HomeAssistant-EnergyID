from homeassistant.helpers.entity import DeviceInfo
from ..const import DOMAIN

import datetime


class EnergyIDAddress:
    def __init__(
            self,
            street: str = None,
            postal_code: str = None,
            city: str = None,
            country: str = None,
    ):
        self.street = street
        self.postal_code = postal_code
        self.city = city
        self.country = country


class EnergyIDRecord:
    def __init__(
            self,
            created: datetime,
            display_name: str,
            record_id: str,
            owner_id: str,
            record_number: str,
            record_type: str,
            time_zone: str,
            last_submission: datetime = None,
            address: EnergyIDAddress = None,
            category: str = None,
            tags: list = None,
            dwelling_type: str = None,
            principal_residence: bool = None,
            occupants: int = None,
            occupier_type: str = None,
            heating_on: str = None,
            auxiliary_heating_on: str = None,
            cooking_on: str = None,
            hot_water_on: str = None,
            floor_surface: float = None,
            year_of_construction: int = None,
            year_of_renovation: int = None,
            energy_performance: float = None,
            energy_rating: float = None,
            energy_efficiency: str = None,
            installations: list = None,
            plan: str = None,
            errors: int = None,
            benchmarking_enabled: bool = None,
            premium_features: list = None,
    ):
        self.created = created
        self.display_name = display_name
        self.record_id = record_id
        self.owner_id = owner_id
        self.record_number = record_number
        self.record_type = record_type
        self.time_zone = time_zone
        self.last_submission = last_submission
        self.address = address
        self.category = category
        self.tags = tags
        self.dwelling_type = dwelling_type
        self.principal_residence = principal_residence
        self.occupants = occupants
        self.occupier_type = occupier_type
        self.heating_on = heating_on
        self.auxiliary_heating_on = auxiliary_heating_on
        self.cooking_on = cooking_on
        self.hot_water_on = hot_water_on
        self.floor_surface = floor_surface
        self.year_of_construction = year_of_construction
        self.year_of_renovation = year_of_renovation
        self.energy_performance = energy_performance
        self.energy_rating = energy_rating
        self.energy_efficiency = energy_efficiency
        self.installations = installations
        self.plan = plan
        self.errors = errors
        self.benchmarking_enabled = benchmarking_enabled
        self.premium_features = premium_features

    @classmethod
    def from_json(cls, json):
        address = None
        if 'address' in json:
            address = EnergyIDAddress(
                json['address']['streetAddress'],
                json['address']['postalCode'],
                json['address']['city'],
                json['address']['country']
            )

        created = None
        if 'created' in json and json['created']:
            created = datetime.datetime.strptime(json['created'], '%Y-%m-%dT%H:%M:%S.%fZ')

        last_submission = None
        if 'lastSubmission' in json and json['lastSubmission'] is not None:
            last_submission = datetime.datetime.strptime(json['lastSubmission'], '%Y-%m-%dT%H:%M:%SZ')

        return cls(
            created=created,
            display_name=json['displayName'],
            record_id=json['id'],
            owner_id=json['ownerId'],
            record_number=json['recordNumber'],
            record_type=json['recordType'],
            time_zone=json['timeZone'],
            last_submission=last_submission,
            address=address,
            category=json['category'] if 'category' in json else None,
            tags=json['tags'] if 'tags' in json else None,
            dwelling_type=json['dwellingType'] if 'dwellingType' in json else None,
            principal_residence=json['principalResidence'] if 'principalResidence' in json else None,
            occupants=json['occupants'] if 'occupants' in json else None,
            occupier_type=json['occupierType'] if 'occupierType' in json else None,
            heating_on=json['heatingOn'] if 'heatingOn' in json else None,
            auxiliary_heating_on=json['auxiliaryHeatingOn'] if 'auxiliaryHeatingOn' in json else None,
            cooking_on=json['cookingOn'] if 'cookingOn' in json else None,
            hot_water_on=json['hotWaterOn'] if 'hotWaterOn' in json else None,
            floor_surface=json['floorSurface'] if 'floorSurface' in json else None,
            year_of_construction=json['yearOfConstruction'] if 'yearOfConstruction' in json else None,
            year_of_renovation=json['yearOfRenovation'] if 'yearOfRenovation' in json else None,
            energy_performance=json['energyPerformance'] if 'energyPerformance' in json else None,
            energy_rating=json['energyRating'] if 'energyRating' in json else None,
            energy_efficiency=json['energyEfficiency'] if 'energyEfficiency' in json else None,
            installations=json['installations'] if 'installations' in json else None,
            plan=json['plan'] if 'plan' in json else None,
            errors=json['errors'] if 'errors' in json else None,
            benchmarking_enabled=json['benchmarkingEnabled'] if 'benchmarkingEnabled' in json else None,
            premium_features=json['premiumFeatures'] if 'premiumFeatures' in json else None,
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            configuration_url=f'https://app.energyid.eu/record/{self.record_number}/facility',
            identifiers={(DOMAIN, f'record-{self.record_id}')},
            name=self.display_name,
            manufacturer="EnergyID",
            model="Record",
        )
