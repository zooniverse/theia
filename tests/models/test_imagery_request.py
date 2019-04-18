from django.test import TestCase
from api.models import ImageryRequest

import sys
sys.dont_write_bytecode = True

class TestImageryRequest(TestCase):
    def setUp(self):
        self.test_request = ImageryRequest()
        self.test_request.dataset_name = 'LANDSAT_8'

    def test_failing(self):
        "it tests stuff"
        assert self.test_request.dataset_name == 'LANDSAT_8'
