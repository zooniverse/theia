from theia.adapters.usgs import ErosWrapper

import pytest
import requests
from unittest import mock
from unittest.mock import patch, PropertyMock


class TestErosWrapper:
    def test_token(self):
        assert(ErosWrapper.token()==None)

    @patch('theia.adapters.usgs.ErosWrapper.token', return_value='aaaaaa')
    @patch('theia.adapters.usgs.ErosWrapper.eros_post')
    def test_token_present(self, mockPost, mockToken):
        result = ErosWrapper.connect()
        assert(result=='aaaaaa')
        mockPost.assert_not_called()

    @patch('theia.adapters.usgs.Utils.get_username', return_value='u')
    @patch('theia.adapters.usgs.Utils.get_password', return_value='p')
    @patch('theia.adapters.usgs.ErosWrapper.token', return_value=None)
    @patch('theia.adapters.usgs.ErosWrapper.eros_post', return_value={'data': 'aaaaaa'})
    def test_successful_connect(self, mockPost, mockToken, mockPassword, mockUsername):
        result = ErosWrapper.connect()
        mockPost.assert_called_once_with('login', {'username': 'u', 'password': 'p'})

    @patch('theia.adapters.usgs.ErosWrapper.token', return_value=None)
    @patch('theia.adapters.usgs.ErosWrapper.eros_post', return_value={'errorCode': 1})
    def test_unsuccessful_connect(self, mockPost, mockToken):
        with pytest.raises(Exception) as connectError:
            result = ErosWrapper.connect()

    def test_access_level(self):
        with mock.patch('theia.adapters.usgs.ErosWrapper.connect'), \
                mock.patch('theia.adapters.usgs.ErosWrapper.eros_post') as mocked:
            ErosWrapper.access_level()
            mocked.assert_called_once_with('', None)

    def test_parse_result_set(self):
        result = ErosWrapper.parse_result_set(None)
        assert result == []

        result = ErosWrapper.parse_result_set([])
        assert result == []

        result = ErosWrapper.parse_result_set(
            [{'displayId': 'aaaa', 'foo': 'bar'}]
        )
        assert result == ['aaaa']

        result = ErosWrapper.parse_result_set(
            [
                {'displayId': 'a', 'foo': 'bar'},
                {'displayId': 'b', 'foo': 'bar'},
            ]
        )
        assert result == ['a', 'b']

        result = ErosWrapper.parse_result_set(
            [
                {'displayId': 'a'},
                {}
            ]
        )
        assert result == ['a']

    def test_eros_prepare(self):
        with mock.patch('theia.adapters.usgs.ErosWrapper.token') as mockToken:
            mockToken.return_value = 'aaaaaa'

            result = ErosWrapper.eros_prepare(None)
            assert result == {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa'},
                'params': {}
            }

            result = ErosWrapper.eros_prepare({'key': 'value'})
            assert result == {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa'},
                'params': {'jsonRequest': '{"key": "value"}'}
            }

            result = ErosWrapper.eros_prepare({'key': 'value'}, params={'foo': 'bar'})
            assert result == {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa'},
                'params': {'foo': 'bar', 'jsonRequest': '{"key": "value"}'}
            }

            result = ErosWrapper.eros_prepare({'key': 'value'}, headers={'X-Foo': 'bar'})
            assert result == {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa', 'X-Foo': 'bar'},
                'params': {'jsonRequest': '{"key": "value"}'}
            }

    @patch('theia.adapters.usgs.ErosWrapper.connect')
    @patch('theia.adapters.usgs.ErosWrapper.eros_prepare', return_value={'prepare': 'result'})
    @patch('theia.adapters.usgs.ErosWrapper.api_url', return_value='api_url')
    @patch('requests.post', autospec=True)
    def test_eros_post(self, mockPost, mockUrl, mockPrepare, mockConnect):
        ErosWrapper.auth_token = None
        with patch.object(mockPost.return_value, 'json', return_value='some json string') as mockJson:
            result = ErosWrapper.eros_post('endpoint', {'foo': 'bar'}, thing='thing')

            mockConnect.assert_called_once()
            mockPrepare.assert_called_once_with({'foo': 'bar'}, thing='thing')
            mockUrl.assert_called_once_with('endpoint')
            mockPost.assert_called_once_with('api_url', prepare='result')
            assert(result=='some json string')

    @patch('theia.adapters.usgs.ErosWrapper.connect')
    @patch('theia.adapters.usgs.ErosWrapper.eros_prepare', return_value={'prepare': 'result'})
    @patch('theia.adapters.usgs.ErosWrapper.api_url', return_value='api_url')
    @patch('requests.get', autospec=True)
    def test_eros_get(self, mockPost, mockUrl, mockPrepare, mockConnect):
        ErosWrapper.auth_token = None
        with patch.object(mockPost.return_value, 'json', return_value='some json string') as mockJson:
            result = ErosWrapper.eros_get('endpoint', {'foo': 'bar'}, thing='thing')

            mockConnect.assert_called_once()
            mockPrepare.assert_called_once_with({'foo': 'bar'}, thing='thing')
            mockUrl.assert_called_once_with('endpoint')
            mockPost.assert_called_once_with('api_url', prepare='result')
            assert(result=='some json string')

    def test_api_url(self):
        assert(ErosWrapper.api_url('foo')=='https://earthexplorer.usgs.gov/inventory/json/v/stable/foo')

    @patch('theia.adapters.usgs.ErosWrapper.eros_post', return_value={'data': 'foo'})
    def test_search_once(self, mockPost):
        result = ErosWrapper.search_once({'search': 'foo'})
        assert(result=='foo')
        mockPost.assert_called_once_with('search', {'search': 'foo'})

    @patch('theia.adapters.usgs.ErosWrapper.search_once', return_value={'results': ['a'], 'lastRecord': 1, 'totalHits': 1})
    @patch('theia.adapters.usgs.ErosWrapper.parse_result_set', return_value=['parsed results'])
    def test_search(self, mockParse, mockSearchOnce):
        result = ErosWrapper.search({'search': 'foo'})

        assert(result==['parsed results'])
        mockSearchOnce.assert_called_once_with({'search': 'foo', 'startingNumber': 0})
        mockParse.assert_called_once_with(['a'])