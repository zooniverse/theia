from theia.adapters.usgs import ErosWrapper

from unittest.mock import patch, PropertyMock, call

class TestErosWrapper:

    @patch('theia.adapters.usgs.Utils.get_username', return_value='Richard Feynman')
    @patch('theia.adapters.usgs.Utils.get_password', return_value='feynmansSuperSecurePassowrd')
    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value={'results': ['LC01_FAKESCENE_007']})
    def test_send_search_request(self, mockRequestSend, mockPassword, mockUsername):
        fakeSearch = {'datasetName' : 'LANDSAT_BAND'}
        ErosWrapper().search(search=fakeSearch)
        mockRequestSend.assert_has_calls([
            call(
                'https://m2m.cr.usgs.gov/api/api/json/stable/login',
                 {'username': 'Richard Feynman', 'password': 'feynmansSuperSecurePassowrd'}
                 ),
            call(
                'https://m2m.cr.usgs.gov/api/api/json/stable/scene-search',
                {'datasetName': 'LANDSAT_BAND'}
            )
        ],
        any_order=False)


    def test_parse_result_set(self):
        wrapper = ErosWrapper()

        result = wrapper.parse_result_set(None)
        assert result == []

        result = wrapper.parse_result_set([])
        assert result == []

        result = wrapper.parse_result_set(
            [{'displayId': 'aaaa', 'foo': 'bar'}]
        )
        assert result == ['aaaa']

        result = wrapper.parse_result_set(
            [
                {'displayId': 'a', 'foo': 'bar'},
                {'displayId': 'b', 'foo': 'bar'},
            ]
        )
        assert result == ['a', 'b']

        result = wrapper.parse_result_set(
            [
                {'displayId': 'a'},
                {}
            ]
        )
        assert result == ['a']

