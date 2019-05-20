from .utils import Utils
from urllib.parse import urljoin
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
        })

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
        if not result_set:
            return []

        return [scene.get('displayId', None) for scene in result_set if 'displayId' in scene]

    @classmethod
    def eros_get(cls, url, request_data, **kwargs):
        if url != 'login' and (not cls.token()):
            cls.connect()

        new_args = cls.eros_prepare(request_data, **kwargs)
        return requests.get(cls.api_url(url), **new_args).json()

    @classmethod
    def eros_post(cls, url, request_data, **kwargs):
        if url != 'login' and (not cls.token()):
            cls.connect()

        new_args = cls.eros_prepare(request_data, **kwargs)
        return requests.post(cls.api_url(url), **new_args).json()

    @classmethod
    def eros_prepare(cls, request_data, **kwargs):
        headers = {'Content-Type': 'application/json'}
        if cls.token():
            headers['X-Auth-Token'] = cls.token()
        if 'headers' in kwargs:
            headers = {**headers, **(kwargs['headers'])}

        params = {}

        if request_data:
            params = {'jsonRequest': json.dumps(request_data)}

        if 'params' in kwargs:
            params = {**params, **(kwargs['params'])}

        new_args = {
            'headers': headers,
            'params': params,
        }

        return {**kwargs, **new_args}
