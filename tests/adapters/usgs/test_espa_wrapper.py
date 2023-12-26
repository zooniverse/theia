from theia.adapters import adapters
from theia.adapters.usgs import EspaWrapper

from unittest import mock
from requests.auth import HTTPBasicAuth

import json


class TestEspaWrapper:
    def test_api_url(self):
        assert EspaWrapper.api_url('foo') == 'https://espa.cr.usgs.gov/api/v0/foo'
        assert EspaWrapper.api_url('') == 'https://espa.cr.usgs.gov/api/v0/'

    def test_espa_credentials(self):
        assert EspaWrapper.espa_credentials(username='u', password='p') == HTTPBasicAuth('u', 'p')

    def test_espa_prepare(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_credentials') as mockCredentials:
            mockCredentials.return_value = {'username': 'password'}
            result = EspaWrapper.espa_prepare(None)

            assert 'headers' in result
            assert 'auth' in result
            assert result['headers'] == {'Content-Type': 'application/json'}
            assert result['auth'] == {'username': 'password'}

        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_credentials') as mockCredentials:
            mockCredentials.return_value = {'username': 'password'}
            result = EspaWrapper.espa_prepare(None, headers={'X-Foo': 'bar'})

            assert 'headers' in result
            assert 'auth' in result
            assert result['headers'] == {'Content-Type': 'application/json', 'X-Foo': 'bar'}
            assert result['auth'] == {'username': 'password'}

    def test_espa_post(self):
        with mock.patch('requests.post') as mockPost, \
                mock.patch('theia.adapters.usgs.EspaWrapper.espa_prepare') as mockPrepare:
            mockPrepare.return_value = {}

            EspaWrapper.espa_post('', None)
            mockPost.assert_called_once_with(EspaWrapper.api_url(''))

            mockPost.reset_mock()
            EspaWrapper.espa_post('', {'foo': 'bar'})
            mockPost.assert_called_once_with(EspaWrapper.api_url(''), json={'foo': 'bar'})

            mockPost.reset_mock()
            EspaWrapper.espa_post('', {'foo': 'bar'}, headers={'X-Foo': 'bar'})
            mockPost.assert_called_once_with(EspaWrapper.api_url(''), json={'foo': 'bar'})

            mockPrepare.return_value = {'foo': 'bar'}
            mockPost.reset_mock()
            EspaWrapper.espa_post('foo', None)
            mockPost.assert_called_once_with(EspaWrapper.api_url('foo'), foo='bar')

    def test_espa_get(self):
        with mock.patch('requests.get') as mockGet, \
                mock.patch('theia.adapters.usgs.EspaWrapper.espa_prepare') as mockPrepare:
            mockPrepare.return_value = {}

            EspaWrapper.espa_get('', None)
            mockGet.assert_called_once_with(EspaWrapper.api_url(''))

            mockGet.reset_mock()
            EspaWrapper.espa_get('', 'payload')
            mockGet.assert_called_once_with(EspaWrapper.api_url('') + 'payload')

            mockGet.reset_mock()
            EspaWrapper.espa_get('', 'payload', headers={'X-Foo': 'bar'})
            mockGet.assert_called_once_with(EspaWrapper.api_url('') + 'payload')

            mockPrepare.return_value = {'foo': 'bar'}
            mockGet.reset_mock()
            EspaWrapper.espa_get('foo', None)
            mockGet.assert_called_once_with(EspaWrapper.api_url('foo'), foo='bar')

    def test_espa_get__eros_down(self):
        with mock.patch('requests.get') as mockGet, \
                mock.patch('theia.adapters.usgs.EspaWrapper.espa_prepare') as mockPrepare:
            mockPrepare.side_effect = json.decoder.JSONDecodeError("We get this exception from the data service when it's down.", mockPrepare, 2)

            try:
                EspaWrapper.espa_get('', None)
                raise AssertionError("This test should have forced espa_get to encounter an exception.")
            except RuntimeError as err:
                assert any(word in str(err) for word in ["EROS", "maintenance", "Wednesdays"])


    def test_list_orders(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = ['orderid_1', 'orderid_2']

            EspaWrapper.list_orders()
            mockGet.assert_called_once_with('list-orders', None)

    def test_order_status(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = {'foo': 'bar', 'status': 'purged'}

            status = EspaWrapper.order_status('1234')
            mockGet.assert_called_once_with('order-status', '1234')
            assert status == 'purged'

    def test_order_one(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_post') as mockPost:
            mockPost.return_value = {'orderid': 'aa1234', 'status': 'ordered'}

            orderid = EspaWrapper.order_one('olitirs8_collection', 'LC08-1234', 'sr')
            mockPost.assert_called_once_with(
                'order',
                {
                    'olitirs8_collection': {
                        'inputs': ['LC08-1234'],
                        'products': ['sr']
                    },
                    'format': 'gtiff'
                }
            )

            assert orderid == 'aa1234'

    def test_locate_collections(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = {
                'olitirs8': { 'products': ['ab', 'sr'] },
                'blah': { 'products': ['blah'] },
                'foo': { 'products': ['sr'] }
            }

            results = EspaWrapper.locate_collections('aaaaa', 'sr')
            mockGet.assert_called_once_with('available-products', 'aaaaa')
            assert results == ['olitirs8', 'foo']

        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = {
                'not_implemented': [ 'LLLLLL' ]
            }

            results = EspaWrapper.locate_collections('aaaaa', 'sr')
            mockGet.assert_called_once_with('available-products', 'aaaaa')
            assert results == []

    def test_order_all(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.locate_collections') as mockFind, \
                mock.patch('theia.adapters.usgs.EspaWrapper.order_one') as mockOrder:

            mockFind.return_value = ['olitirs8']
            mockOrder.side_effect = ['order1']

            orders = EspaWrapper.order_all('LC08', 'sr')
            mockFind.assert_called_once_with('LC08', 'sr')

            assert mockOrder.call_count == 1
            mockOrder.assert_called_once_with('olitirs8', 'LC08', 'sr')
            assert orders == [ {'scene_entity_id': 'LC08', 'scene_order_id': 'order1'}, ]

    def test_download_urls(self):
        with mock.patch('theia.adapters.usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = {
                'order1234': [
                    {'product_dload_url': 'url1'},
                    {'product_dload_url': 'url2'}
                ]
            }

            urls = EspaWrapper.download_urls('order1234')
            mockGet.assert_called_once_with('item-status', 'order1234')
            assert urls == ['url1', 'url2']
