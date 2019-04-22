from urllib.parse import urljoin
from os import environ
import json
import requests


class ErosWrapper():
    auth_token = None

    @classmethod
    def connect(cls, username=environ['USGS_USERNAME'], password=environ['USGS_PASSWORD']):
        auth_data = {
            'username': username,
            'password': password
        }

        response = cls.eros_post('login', auth_data)

        if not response['errorCode']:
            cls.auth_token = response['data']

        return cls.auth_token

    @classmethod
    def access_level(cls):
        response = cls.eros_post('', {})
        return response['access_level']

    @classmethod
    def search(cls, search):
        result = []
        data = {'lastRecord': 0, 'nextRecord': 0, 'totalHits': 1}
        while data['lastRecord'] < data['totalHits']:
            search['startingNumber'] = data['nextRecord']
            data = cls.search_once(search)
            result = result + cls.parse_result_set(data['results'])
        return result

    @classmethod
    def search_once(cls, search):
        response = cls.eros_post('search', search)
        return response['data']

    @classmethod
    def api_url(cls, path):
        # return urljoin('https://demo1580318.mockable.io/', path)
        return urljoin('https://earthexplorer.usgs.gov/inventory/json/v/stable/', path)

    @classmethod
    def parse_result_set(cls, result_set):
        return [scene['displayId'] for scene in result_set]

    @classmethod
    def eros_get(cls, url, request_data, **kwargs):
        if url != 'login' and (not cls.auth_token):
            cls.connect()

        new_args = cls.eros_prepare(request_data, **kwargs)
        return requests.get(cls.api_url(url), **new_args).json()

    @classmethod
    def eros_post(cls, url, request_data, **kwargs):
        if url != 'login' and (not cls.auth_token):
            cls.connect()

        new_args = cls.eros_prepare(request_data, **kwargs)
        return requests.post(cls.api_url(url), **new_args).json()

    @classmethod
    def eros_prepare(cls, request_data, **kwargs):
        headers = {'Content-Type': 'application/json'}
        if cls.auth_token:
            headers['X-Auth-Token'] = cls.auth_token
        if 'headers' in kwargs:
            headers = {**headers, **(kwargs[headers])}

        params = {'jsonRequest': json.dumps(request_data)}
        if 'params' in kwargs:
            params = {**params, **(kwargs[params])}

        new_args = {
            'headers': headers,
            'params': params,
        }

        return {**new_args, **kwargs}