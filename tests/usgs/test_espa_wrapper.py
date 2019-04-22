from usgs import EspaWrapper
from unittest import mock


class TestEspaWrapper:
    def test_api_url(self):
        assert EspaWrapper.api_url('foo') == 'https://espa.cr.usgs.gov/api/v1/foo'
        assert EspaWrapper.api_url('') == 'https://espa.cr.usgs.gov/api/v1/'
