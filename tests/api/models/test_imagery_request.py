from django.test import TestCase
from theia.api.models import ImageryRequest
from datetime import datetime


class TestImageryRequest(TestCase):
    def setUp(self):
        self.test_request = ImageryRequest(
            dataset_name='LANDSAT_8_C1',
            project_id=123,
            created_at=datetime.fromisoformat('2019-05-17')
        )

    def test___str__(self):
        assert '[ImageryRequest project 123 at 2019-05-17]' == self.test_request.__str__()

    def test_post_create(self):
        '''it enqueues a job after being created'''
        # TODO: write this test soon
        assert True
