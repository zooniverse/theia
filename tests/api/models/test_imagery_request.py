import pytest
from unittest.mock import patch

from django.test import TestCase
from theia.api.models import ImageryRequest
from datetime import datetime

import theia.tasks


class TestImageryRequest(TestCase):
    def setUp(self):
        self.test_request = ImageryRequest(
            id=3,
            dataset_name='LANDSAT_8_C1',
            project_id=123,
            created_at=datetime.fromisoformat('2019-05-17')
        )

    def test___str__(self):
        assert '[ImageryRequest project 123 at 2019-05-17]' == self.test_request.__str__()

    def test_post_create(self):
        '''it enqueues a job after being created'''
        with patch.object(theia.tasks, 'locate_scenes', autospec=True) as mockLocate:
            with patch.object(mockLocate.return_value, 'delay', autospec=True) as mockDelay:
                ImageryRequest.post_save(None, self.test_request, False)
                mockDelay.assert_not_called()

                ImageryRequest.post_save(None, self.test_request, True)
                mockDelay.assert_called_once_with(self.test_request.id)
