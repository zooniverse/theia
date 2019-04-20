from urllib.parse import urljoin
from os import environ
import json
import requests


class ErosWrapper():
    auth_token = None

    @classmethod
    def connect(self):
        auth_data = {
            'username': environ['USGS_USERNAME'],
            'password': environ['USGS_PASSWORD']
        }

        response = requests.post(
            self.api_url('login'),
            params={
                "jsonRequest": json.dumps(auth_data)
            },
            headers={
                "Content-Type": "application/json"
            }
        ).json()

        if not response['errorCode']:
            self.auth_token = response['data']

        return self.auth_token

    @classmethod
    def access_level(self):
        print(self)
        if not self.auth_token:
            self.connect()

        print(self.auth_token)
        response = requests.post(
            self.api_url(''),
            headers={
                "X-Auth-Token": self.auth_token
            }
        ).json()

        return response['access_level']

    @classmethod
    def api_url(self, path):
        return urljoin('https://earthexplorer.usgs.gov/inventory/json/v/stable/', path)
