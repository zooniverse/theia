import pytest
from unittest.mock import patch
from theia.utils import PanoptesUtils

class TestUtils:
    @patch('os.getenv', return_value='client_id')
    def test_client_id(self, mockGetenv):
        assert(PanoptesUtils.client_id()=='client_id')

    @patch('os.getenv', return_value='client_secret')
    def test_client_secret(self, mockGetenv):
        assert(PanoptesUtils.client_secret()=='client_secret')

    @patch('os.getenv', return_value='https://example.org')
    def test_url(self, mockGetenv):
        assert(PanoptesUtils.url('some/path')=='https://example.org/some/path')

    @patch('os.getenv', return_value='https://example.org')
    def test_base_url(self, mockGetenv):
        assert(PanoptesUtils.base_url()=='https://example.org')
