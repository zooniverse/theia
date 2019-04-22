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
            mockPost.assert_called_once_with(EspaWrapper.api_url(''))

            mockPost.reset_mock()
            EspaWrapper.espa_post('', {'foo': 'bar'}, headers={'X-Foo': 'bar'})
            mockPost.assert_called_once_with(EspaWrapper.api_url(''))
