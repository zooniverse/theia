import pytest
from unittest.mock import patch, Mock

from theia.utils import PanoptesOAuth2

class TestPanoptesOauth2:
    def test_get_user_id(self):
        auth = PanoptesOAuth2()
        assert(auth.get_user_id({'username': 'user name', 'other field': 'foo'}, {})=='user name')

    @patch('panoptes_client.Panoptes.get', return_value=[{'users': [{
        'login': 'some login',
        'email': 'some email',
        'admin': 'False'
    }]}])
    def test_get_user_details(self, mockGet):
        auth = PanoptesOAuth2()
        result = auth.get_user_details({
            'access_token': 'at',
            'refresh_token': 'rt',
            'expires_in': 60
        })
        assert(result['username']=='some login')
        assert(result['email']=='some email')