import pytest
from unittest.mock import patch, Mock
from typing import NamedTuple

from theia.utils import PanoptesOAuth2

class FakeProject():
    def __init__(self, id, href='default.org'):
        self.id = id
        self.href = href

class TestPanoptesOauth2:
    def test_get_user_id(self):
        auth = PanoptesOAuth2()
        assert(auth.get_user_id({'username': 'user name', 'other field': 'foo'}, {})=='user name')

    @patch('panoptes_client.Panoptes.get', return_value=[{'users': [{
        'login': 'some login',
        'email': 'some email',
        'admin': False
    }]}])
    @patch('panoptes_client.Project.where', return_value=[
        FakeProject(id='1'),
        FakeProject(id='2'),
    ])
    def test_get_user_details(self, mockProject, mockGet):
        auth = PanoptesOAuth2()
        result = auth.get_user_details({
            'access_token': 'at',
            'refresh_token': 'rt',
            'expires_in': 60
        })
        assert(result['username']=='some login')
        assert(result['email']=='some email')
