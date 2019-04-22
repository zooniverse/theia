from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth
import json
import requests
from os import environ


class EspaWrapper:
    @classmethod
    def api_url(cls, path):
        # return urljoin('https://demo1580318.mockable.io/', path)
        return urljoin('https://espa.cr.usgs.gov/api/v1/', path)

    @classmethod
    def list_orders(cls):
        return cls.espa_get('list-orders', None)

    @classmethod
    def order_status(cls, order_id):
        return cls.espa_get('order-status', order_id)['status']

    @classmethod
    def espa_get(cls, url, request_data, **kwargs):
        new_args = cls.espa_prepare(request_data, **kwargs)
        new_url = cls.api_url(url)
        if request_data:
            new_url = urljoin(new_url, cls.sanitize_payload(request_data))
        return requests.get(new_url, **new_args).json()

    @classmethod
    def espa_post(cls, url, request_data, **kwargs):
        new_args = cls.espa_prepare(request_data, **kwargs)
        new_url = cls.api_url(url)
        if request_data:
            new_url = urljoin(new_url, cls.sanitize_payload(request_data))
        return requests.post(new_url, **new_args).json()

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
    def espa_credentials(cls, username=environ['USGS_USERNAME'], password=environ['USGS_PASSWORD']):
        return HTTPBasicAuth(username, password)

    @classmethod
    def sanitize_payload(cls, payload):
        if isinstance(payload, str):
            return payload
        else:
            return json.dumps(payload)
