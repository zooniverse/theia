import pytest
from unittest.mock import patch
from theia.operations.panoptes_operations import PanoptesUtils

class TestUtils:
    @patch('os.getenv', return_value='client_id')
    def test_client_id(self, mockGetenv):
        assert(PanoptesUtils.client_id()=='client_id')

    @patch('os.getenv', return_value='client_secret')
    def test_client_secret(self, mockGetenv):
        assert(PanoptesUtils.client_secret()=='client_secret')

    @patch('os.getenv', return_value='url')
    def test_url(self, mockGetenv):
        assert(PanoptesUtils.url()=='url')
