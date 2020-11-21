from .utils import Utils
from urllib.parse import urljoin, quote
from os import environ
import json
import requests


class ErosWrapper():
    auth_token = None

    @classmethod
    def token(cls):
        return cls.auth_token

    @classmethod
    def connect(cls):
        if cls.token():
            return cls.token()

        response = cls.eros_post('login', {
            'username': Utils.get_username(),
            'password': Utils.get_password()
        }, authenticating=True)

        if not response.get('errorCode'):
            cls.auth_token = response.get('data')
        else:
            raise Exception()

        return cls.token()

    @classmethod
    def access_level(cls):
        response = cls.eros_post('', None)
        return response['access_level']

    @classmethod
    def search(cls, search):
        search = {
            "datasetName": "LANDSAT_8_C1",
            "metadataFilter": {
                "filterType": "and",
                "childFilters": [
                    {
                        "filterType": "value",
                        "filterId": "5e83d0b81d20cee8",
                        "value": "23"
                    },
                    {
                        "filterType": "value",
                        "filterId": "5e83d0b849ed5ee7",
                        "value": "47"
                    },
                    {
                        "filterType": "value",
                        "filterId": "5e83d0b83a03f8ee",
                        "value": "DAY"
                    }
                ]
            },
            "cloudCoverFilter": {
                "max": 45,
                "min": 0
            },
            "startingNumber": 0
        }

        result = []
        data = {'lastRecord': 0, 'nextRecord': 0, 'totalHits': 1}
        while data['lastRecord'] < data['totalHits']:
            search['startingNumber'] = data['nextRecord']
            data = cls.search_once(search)
            print("DATA")
            print(data)
            result = result + cls.parse_result_set(data['results'])
        return result

    @classmethod
    def search_once(cls, search):
        if not cls.token():
            cls.connect()

        new_args = cls.eros_prepare(search)
        response = requests.post("https://m2m.cr.usgs.gov/api/api/json/stable/scene-search", **new_args).json()

        print("SO EROS SAYS: ")
        print(response)
        return response['data']

    @classmethod
    def api_url(cls, path):
        # return urljoin('https://demo1580318.mockable.io/', path)
        return urljoin('https://earthexplorer.usgs.gov/inventory/json/v/1.3.0/', path)

    @classmethod
    def parse_result_set(cls, result_set):
        if not result_set:
            return []

        return [scene.get('displayId', None) for scene in result_set if 'displayId' in scene]

    @classmethod
    def eros_get(cls, url, request_data, authenticating=False, **kwargs):
        if url != 'login' and (not cls.token()):
            cls.connect()

        new_args = cls.eros_prepare(request_data, authenticating=authenticating, **kwargs)
        return requests.get(cls.api_url(url), **new_args).json()

    @classmethod
    def eros_post(cls, url, request_data, authenticating=False, **kwargs):
        if url != 'login' and (not cls.token()):
            cls.connect()

        new_args = cls.eros_prepare(request_data, authenticating=authenticating, **kwargs)
        return requests.post(cls.api_url(url), **new_args).json()

    @classmethod
    def eros_prepare(cls, request_data, authenticating=False, **kwargs, ):
        headers = {}
        if cls.token():
            headers['X-Auth-Token'] = cls.token()
        if 'headers' in kwargs:
            headers = {**headers, **(kwargs['headers'])}

        params = {}
        if 'params' in kwargs:
            params = {**params, **(kwargs['params'])}

        if authenticating:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            if request_data:
                data = 'jsonRequest=' + quote(json.dumps(request_data))

            new_args = {
                'headers': headers,
                'data': data,
            }
        else:
            headers['Content-Type'] = 'application/json'

            if request_data:
                params = {'jsonRequest': json.dumps(request_data)}

            new_args = {
                'headers': headers,
                'params': params,
            }

        return {**kwargs, **new_args}
