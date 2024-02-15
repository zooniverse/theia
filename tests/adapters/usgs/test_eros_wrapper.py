from theia.adapters.usgs import ErosWrapper
from unittest.mock import patch, call
import datetime
THREE_HOURS_AGO = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
FAKE_SEARCH = {'datasetName' : 'LANDSAT_BAND'}

class TestErosWrapper:
    def test_is_token_expired_no_login_time(self):
        is_expired = ErosWrapper().is_token_expired()
        assert is_expired == True

    def test_is_token_expired_login_time_past_expiry(self):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = THREE_HOURS_AGO
        assert eros_wrapper.is_token_expired() == True

    def test_is_token_expired_login_time_not_expired(self):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        assert eros_wrapper.is_token_expired() == False

    @patch('theia.adapters.usgs.Utils.get_username', return_value='Richard Feynman')
    @patch('theia.adapters.usgs.Utils.get_password', return_value='feynmansSuperSecurePassowrd')
    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=200)
    def test_login_no_login_time(self, mock_send_request, *_):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login()
        mock_send_request.assert_has_calls([
            call(
                'https://m2m.cr.usgs.gov/api/api/json/stable/login',
                 {'username': 'Richard Feynman', 'password': 'feynmansSuperSecurePassowrd'}
                 )
        ])

    @patch('theia.adapters.usgs.Utils.get_username', return_value='Richard Feynman')
    @patch('theia.adapters.usgs.Utils.get_password', return_value='feynmansSuperSecurePassowrd')
    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=200)
    def test_login_token_expired(self, mock_send_request, *_):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login()
        mock_send_request.assert_has_calls([
            call(
                'https://m2m.cr.usgs.gov/api/api/json/stable/login',
                 {'username': 'Richard Feynman', 'password': 'feynmansSuperSecurePassowrd'}
                 )
        ])

    @patch('theia.adapters.usgs.ErosWrapper.send_request')
    def test_login_not_called_when_token_not_expired(self, mock_send_request):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        eros_wrapper.login()
        mock_send_request.assert_not_called()

    @patch('theia.adapters.usgs.Utils.get_username', return_value='Richard Feynman')
    @patch('theia.adapters.usgs.Utils.get_password', return_value='feynmansSuperSecurePassowrd')
    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value={'results': ['LC01_FAKESCENE_007']})
    def test_send_search_request(self, mockRequestSend, *_):
        ErosWrapper().search(search=FAKE_SEARCH)
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

    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=200)
    def test_add_scene_to_order_list(self, mock_send_request):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        eros_wrapper.add_scenes_to_order_list(scene_id=1, search=FAKE_SEARCH)
        mock_send_request.assert_has_calls([
            call(
                'https://m2m.cr.usgs.gov/api/api/json/stable/scene-list-add',
                 {'listId': 1, 'idField': 'displayId', 'entityId': 1, 'datasetName': 'LANDSAT_BAND'}
            )
        ],
        any_order=False)

    @patch('theia.adapters.usgs.ErosWrapper.login')
    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=200)
    def test_add_scene_to_order_list_logs_in(self, _, mock_login):
        eros_wrapper = ErosWrapper()
        eros_wrapper.add_scenes_to_order_list(scene_id=1, search=FAKE_SEARCH)
        mock_login.assert_called_once()

    @patch('theia.adapters.usgs.ErosWrapper.login')
    @patch('theia.adapters.usgs.ErosWrapper.send_request')
    def test_available_products_logs_in(self, _, mock_login):
        eros_wrapper = ErosWrapper()
        eros_wrapper.available_products(list_id=1, search=FAKE_SEARCH)
        mock_login.assert_called_once()

    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=[{'bulkAvailable': True, 'downloadSystem': 'dds', 'entityId': 'LC01_FAKESCENE_007', 'displayId': 'LC01FAKESCENE007', 'id': 1}])
    def test_available_products(self, mock_send_request):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        avail_products = eros_wrapper.available_products(list_id=1, search=FAKE_SEARCH)
        mock_send_request.assert_has_calls([
            call(
                'https://m2m.cr.usgs.gov/api/api/json/stable/download-options',
                 {'listId': 1, 'datasetName': 'LANDSAT_BAND'}
            )
        ],
        any_order=False)
        assert len(avail_products) == 1
        assert avail_products[0] == {
            'entityId': 'LC01_FAKESCENE_007',
            'productId': 1,
            'displayId': 'LC01FAKESCENE007'
        }

    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=[])
    def test_available_products_has_no_results(self, _):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        avail_products = eros_wrapper.available_products(list_id=1, search=FAKE_SEARCH)
        assert avail_products == []

    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=[{'bulkAvailable': False, 'downloadSystem': 'dds', 'entityId': 'LC01_FAKESCENE_007', 'displayId': 'LC01FAKESCENE007', 'id': 1}])
    def test_avail_products_result_not_available(self, _):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        avail_products = eros_wrapper.available_products(list_id=1, search=FAKE_SEARCH)
        assert avail_products == []

    @patch('theia.adapters.usgs.ErosWrapper.send_request', return_value=[{'bulkAvailable': True, 'downloadSystem': 'folder', 'entityId': 'LC01_FAKESCENE_007', 'displayId': 'LC01FAKESCENE007', 'id': 1}])
    def test_avail_products_result_download_system_incorrect(self, _):
        eros_wrapper = ErosWrapper()
        eros_wrapper.login_time = datetime.datetime.utcnow()
        avail_products = eros_wrapper.available_products(list_id=1, search=FAKE_SEARCH)
        assert avail_products == []

