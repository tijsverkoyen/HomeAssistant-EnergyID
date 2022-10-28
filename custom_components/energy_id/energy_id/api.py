"""API client for EnergyID API."""
import urllib.parse

from requests import get, HTTPError

from .meter import EnergyIDMeter
from .record import EnergyIDRecord

import logging

_LOGGER = logging.getLogger(__name__)


class EnergyIDApi:
    def __init__(self, host: str, api_key: str):
        self._host = host
        self._api_key = api_key

    def get_record(self, record: str, expand: list = None):
        params = None
        if expand is not None:
            params = {
                "expand": ",".join(expand)
            }

        response = self._do_call(
            'GET',
            f'api/v1/records/{record}',
            params=params
        )

        return EnergyIDRecord(
            response['id'],
            response['recordNumber'],
            response['displayName']
        )

    def get_record_meters(self, record: str, expand: list = None):
        params = None
        if expand is not None:
            params = {
                "expand": ",".join(expand)
            }

        response = self._do_call(
            'GET',
            f'api/v1/records/{record}/meters',
            params=params
        )

        data = []
        for meter_data in response:
            data.append(
                EnergyIDMeter(
                    meter_data['id'],
                    meter_data['recordId'],
                    meter_data['displayName'],
                    meter_data['meterType'],
                    meter_data['metric'],
                    meter_data['multiplier'],
                    meter_data['readingType'],
                    meter_data['theme'],
                    meter_data['unit']
                )
            )

        return data

    def get_meter_readings(self, meter: str, take: int = 20, next_row_key: str = None):
        params = {
            "take": take
        }
        if next_row_key is not None:
            params['nextRowKey'] = next_row_key

        return self._do_call(
            'GET',
            f'api/v1/Meters/{meter}/readings',
            params=params
        )

    def _do_call(self, method: str, path: str, **kwargs) -> dict:
        """Make a request."""
        headers = kwargs.get("headers")
        json = kwargs.get("json")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
        if json is None:
            json = {}
        else:
            json = dict(json)

        headers["authorization"] = 'apikey ' + self._api_key

        try:
            if method == 'GET':
                url = f'{self._host}/{path}'
                if kwargs.get("params") is not None:
                    url = f'{url}?{urllib.parse.urlencode(kwargs.get("params"))}'

                response = get(url, headers=headers, json=json)
                response.raise_for_status()
                json_data = response.json()
                _LOGGER.debug(f'JSON data for {url}: {json_data}')

            return response.json()

        except HTTPError as error:
            _LOGGER.error(error)
            raise EnergyIDApiError(f'HTTP Error: {error}')


class EnergyIDApiError(Exception):
    pass
