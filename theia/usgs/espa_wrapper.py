from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import requests
from os import environ


class EspaWrapper:
    @classmethod
    def api_url(cls, path):
        # return urljoin('https://demo1580318.mockable.io/', path)
        return urljoin('https://espa.cr.usgs.gov/api/v1/', path)

    @classmethod
    def espa_prepare(cls, request_data, **kwargs):
        headers = {'Content-Type': 'application/json'}
        if 'headers' in kwargs:
            headers = {**headers, **(kwargs['headers'])}

        auth = cls.espa_credentials()

        new_args = {
            'headers': headers,
            'auth': auth
        }
        return {**kwargs, **new_args}

    @classmethod
    def espa_post(cls, url, request_data, **kwargs):
        new_args = cls.espa_prepare(request_data, **kwargs)
        return requests.post(cls.api_url(url), **new_args).json()

    @classmethod
    def list_orders(cls):
        return

    @classmethod
    def espa_credentials(cls, username=environ['USGS_USERNAME'], password=['USGS_PASSWORD']):
        return HTTPBasicAuth(username, password)
