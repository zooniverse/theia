
from django.test import TestCase
from theia.api.models import RequestedScene
from datetime import datetime


class TestRequestedScene(TestCase):
    def test___str__(self):
        instance = RequestedScene(scene_entity_id='foo', scene_url='foo_url')
        assert instance.__str__() == '[RequestedScene foo status 0]'