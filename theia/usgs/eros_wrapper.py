from urllib.parse import urljoin
from os import environ
import json
import requests


class ErosWrapper():
    auth_token = None

    @classmethod
    def connect(cls):
        auth_data = {
            'username': environ['USGS_USERNAME'],
            'password': environ['USGS_PASSWORD']
        }

        response = requests.post(
            cls.api_url('login'),
            params={
                "jsonRequest": json.dumps(auth_data)
            },
            headers={
                "Content-Type": "application/json"
            }
        ).json()

        if not response['errorCode']:
            cls.auth_token = response['data']

        return cls.auth_token

    @classmethod
    def access_level(cls):
        if not cls.auth_token:
            cls.connect()

        response = requests.post(
            cls.api_url(''),
            headers={
                "X-Auth-Token": cls.auth_token
            }
        ).json()

        return response['access_level']

    @classmethod
    def search(cls, search):
        if not cls.auth_token:
            cls.connect()

        result = []
        data = {'lastRecord': 0, 'nextRecord': 0, 'totalHits': 1}
        while data['lastRecord'] < data['totalHits']:
            startingNumber = data['nextRecord']
            search['startingNumber'] = startingNumber
            data = cls.search_once(search)
            result = result + cls.parse_result_set(data['results'])
        return result

    @classmethod
    def search_once(cls, search):
        print('search once')
        if not cls.auth_token:
            cls.connect()

        response = requests.post(
            cls.api_url('search'),
            params={
                'jsonRequest': json.dumps(search)
            },
            headers={
                "X-Auth-Token": cls.auth_token
            }
        ).json()

        return response['data']

    @classmethod
    def api_url(cls, path):
        # return urljoin('https://demo1580318.mockable.io/', path)
        return urljoin('https://earthexplorer.usgs.gov/inventory/json/v/stable/', path)

    @classmethod
    def parse_search_results(cls, search):
        return

    @classmethod
    def parse_result_set(cls, result_set):
        return [scene['displayId'] for scene in result_set]