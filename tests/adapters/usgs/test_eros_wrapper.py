from theia.adapters.usgs import ErosWrapper
from unittest import mock


class TestErosWrapper:
    def test_connect(self):
        with mock.patch('theia.adapters.usgs.ErosWrapper.token') as mockToken, \
                mock.patch('theia.adapters.usgs.ErosWrapper.eros_post') as mockPost:
            mockToken.return_value='aaaaaa'
            result = ErosWrapper.connect({'username': 'u', 'password': 'p'})

            mockPost.assert_not_called
            assert mockToken.call_count == 2

        with mock.patch('theia.adapters.usgs.ErosWrapper.eros_post') as mocked:
            ErosWrapper.connect(username='u', password='p')
            mocked.assert_called_once_with('login', {'username': 'u', 'password': 'p'})

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
            mockToken.return_value='aaaaaa'

            result = ErosWrapper.eros_prepare(None)
            assert result ==  {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa'},
                'params': {}
            }

            result = ErosWrapper.eros_prepare({'key': 'value'})
            assert result ==  {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa'},
                'params': { 'jsonRequest': '{"key": "value"}' }
            }

            result = ErosWrapper.eros_prepare({'key': 'value'}, params={'foo': 'bar'})
            assert result ==  {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa'},
                'params': { 'foo': 'bar', 'jsonRequest': '{"key": "value"}'}
            }

            result = ErosWrapper.eros_prepare({'key': 'value'}, headers={'X-Foo': 'bar'})
            assert result ==  {
                'headers': {'Content-Type': 'application/json', 'X-Auth-Token': 'aaaaaa', 'X-Foo': 'bar'},
                'params': {'jsonRequest': '{"key": "value"}'}
            }
