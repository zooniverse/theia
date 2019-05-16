import pytest
from unittest.mock import patch
from django.db.models import Model

from theia.adapters.usgs import Adapter, ErosWrapper, EspaWrapper, ImagerySearch
from theia.api.models import ImageryRequest, JobBundle, RequestedScene

from unittest import mock

class TestUsgsAdapter:
    def test_enum_datasets(self):
        assert(not Adapter.enum_datasets())

    def test_acquire_image(self):
        assert(not Adapter.acquire_image({}))

    def test_resolve_image(self):
        bundle = JobBundle(scene_entity_id='LC08')
        assert(Adapter.resolve_image(bundle, 'aerosol') == 'LC08_sr_aerosol.tif')

    @pytest.mark.focus
    def test_process_request(self):
        dummyRequest = RequestedScene(id=3)
        with mock.patch('theia.adapters.usgs.ImagerySearch.build_search') as mockBuild, \
                mock.patch('theia.adapters.usgs.ErosWrapper.search') as mockSearch, \
                mock.patch('theia.adapters.usgs.EspaWrapper.order_all') as mockOrderAll, \
                mock.patch('theia.api.models.RequestedScene.objects.create') as mockRSO, \
                mock.patch('theia.adapters.usgs.tasks.wait_for_scene.delay') as mockWait:

            mockBuild.return_value = {}
            mockSearch.return_value = ['some scene id']
            mockOrderAll.return_value = [{}]
            mockRSO.return_value = dummyRequest

            request = ImageryRequest()
            Adapter.process_request(request)

            mockBuild.assert_called_once_with(request)
            mockSearch.assert_called_once_with({})
            mockOrderAll.assert_called_once_with('some scene id', 'sr')
            mockRSO.assert_called_once()
            mockWait.assert_called_once_with(3)
