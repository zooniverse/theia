from django.test import TestCase
from api.models import ImageryRequest
from datetime import datetime

import sys
sys.dont_write_bytecode = True

class TestImageryRequest(TestCase):
    def setUp(self):
        self.test_request = ImageryRequest(dataset_name='LANDSAT_8', project_id=123, created_at=datetime.fromisoformat('2019-05-17'))

    def test___str__(self):
        assert '[ImageryRequest project 123 at 2019-05-17]' == self.test_request.__str__()