from usgs import EspaWrapper
from unittest import mock
from requests.auth import HTTPBasicAuth


class TestEspaWrapper:
    def test_api_url(self):
        assert EspaWrapper.api_url('foo') == 'https://espa.cr.usgs.gov/api/v1/foo'
        assert EspaWrapper.api_url('') == 'https://espa.cr.usgs.gov/api/v1/'

    def test_espa_credentials(self):
        assert EspaWrapper.espa_credentials(username='u', password='p') == HTTPBasicAuth('u','p')

    def test_espa_prepare(self):
        with mock.patch('usgs.EspaWrapper.espa_credentials') as mockCredentials:
            mockCredentials.return_value = {'username': 'password'}
            result = EspaWrapper.espa_prepare(None)

            assert 'headers' in result
            assert 'auth' in result
            assert result['headers'] == {'Content-Type': 'application/json'}
            assert result['auth'] == {'username': 'password'}

        with mock.patch('usgs.EspaWrapper.espa_credentials') as mockCredentials:
            mockCredentials.return_value = {'username': 'password'}
            result = EspaWrapper.espa_prepare(None, headers={'X-Foo': 'bar'})

            assert 'headers' in result
            assert 'auth' in result
            assert result['headers'] == {'Content-Type': 'application/json', 'X-Foo': 'bar'}
            assert result['auth'] == {'username': 'password'}

    def test_espa_post(self):
        with mock.patch('requests.post') as mockPost, \
                mock.patch('usgs.EspaWrapper.espa_prepare') as mockPrepare:
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
                mock.patch('usgs.EspaWrapper.espa_prepare') as mockPrepare:
            mockPrepare.return_value = {}

            EspaWrapper.espa_get('', None)
            mockGet.assert_called_once_with(EspaWrapper.api_url(''))

            mockGet.reset_mock()
            EspaWrapper.espa_get('', 'payload')
            mockGet.assert_called_once_with(EspaWrapper.api_url('')+'payload')

            mockGet.reset_mock()
            EspaWrapper.espa_get('', 'payload', headers={'X-Foo': 'bar'})
            mockGet.assert_called_once_with(EspaWrapper.api_url('')+'payload')

            mockPrepare.return_value = {'foo': 'bar'}
            mockGet.reset_mock()
            EspaWrapper.espa_get('foo', None)
            mockGet.assert_called_once_with(EspaWrapper.api_url('foo'), foo='bar')

    def test_list_orders(self):
        with mock.patch('usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = ['orderid_1', 'orderid_2']

            EspaWrapper.list_orders()
            mockGet.assert_called_once_with('list-orders', None)

    def test_order_status(self):
        with mock.patch('usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = {'foo': 'bar', 'status': 'purged'}

            status = EspaWrapper.order_status('1234')
            mockGet.assert_called_once_with('order-status', '1234')
            assert status == 'purged'

    def test_order(self):
        with mock.patch('usgs.EspaWrapper.espa_post') as mockPost:
            mockPost.return_value = {'orderid': 'aa1234', 'status': 'ordered'}

            orderid = EspaWrapper.order('olitirs8_collection','LC08-1234', 'sr')
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

    def test_available_products(self):
        with mock.patch('usgs.EspaWrapper.espa_get') as mockGet:
            mockGet.return_value = {
                'olitirs8': {
                    'products': ['ab', 'sr']
                },
                'blah': {
                    'products': ['blah']
                },
                'foo': {
                    'products': ['sr']
                }
            }

            results = EspaWrapper.available_products('aaaaa', 'sr')
            mockGet.assert_called_once_with('available-products', 'aaaaa')
            assert results == [
                ['olitirs8', 'aaaaa', 'sr'],
                ['foo', 'aaaaa', 'sr']
            ]
