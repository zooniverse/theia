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
    def locate_collections(cls, scene_id, desired_product_id):
        results = cls.espa_get('available-products', scene_id)
        return [collection for collection
            in results
            if cls._product_is_available(desired_product_id, results[collection])]

    @classmethod
    def _product_is_available(cls, product_id, result_dict):
        return \
            isinstance(result_dict, dict) and \
            result_dict['products'] and \
            product_id in result_dict['products']

    @classmethod
    def order_status(cls, order_id):
        return cls.espa_get('order-status', order_id)['status']

    @classmethod
    def order_one(cls, collection, scene_id, product_type):
        return cls.espa_post('order', {
            collection: {
                'inputs': [scene_id],
                'products': [product_type]
            },
            'format': 'gtiff'
        })['orderid']

    @classmethod
    def order_all(cls, scene_id, product_type):
        return [
            {
                'scene_entity_id': scene_id,
                'scene_order_id': cls.order_one(
                    collection,
                    scene_id,
                    product_type
                )
            }
            for collection
            in cls.locate_collections(scene_id, product_type)
        ]

    @classmethod
    def download_urls(cls, order_id):
        result = cls.espa_get('item-status', order_id)
        return [item['product_dload_url'] for item in result[order_id]]

    @classmethod
    def espa_get(cls, url, request_data, **kwargs):
        new_args = cls.espa_prepare(request_data, **kwargs)
        new_url = cls.api_url(url)
        if request_data:
            new_url = urljoin(new_url + '/', request_data)
        return requests.get(new_url, **new_args).json()

    @classmethod
    def espa_post(cls, url, request_data, **kwargs):
        new_args = cls.espa_prepare(request_data, **kwargs)
        new_url = cls.api_url(url)
        if request_data:
            new_args = {**new_args, **{'json': request_data}}
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
