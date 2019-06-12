import pytest
from unittest import mock
from unittest.mock import patch, PropertyMock
import numpy as np

from theia.adapters.usgs import Adapter, ErosWrapper, EspaWrapper, ImagerySearch
from theia.api.models import ImageryRequest, JobBundle, RequestedScene

import tarfile

class TestUsgsAdapter:
    def test_enum_datasets(self):
        assert(not Adapter.enum_datasets())

    def test_acquire_image(self):
        assert(not Adapter.acquire_image({}))

    def test_resolve_image(self):
        request = ImageryRequest(adapter_name='usgs', dataset_name='LANDSAT_8_C1')
        bundle = JobBundle(scene_entity_id='LC08', imagery_request=request)
        assert(Adapter.resolve_image(bundle, 'aerosol') == 'LC08_sr_aerosol.tif')

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

    @patch('os.path.isfile', return_value=False)
    @patch('platform.uname_result.node', new_callable=PropertyMock, return_value='testhostname')
    @patch('theia.api.models.JobBundle.save')
    @patch('urllib.request.urlretrieve')
    @patch('theia.utils.FileUtils.untar')
    def test_retrieve(self, mockExtract, mockRetrieve, mockSave, mockUnameNode, mockIsFile):
        scene = RequestedScene(scene_url='https://example.org')
        bundle = JobBundle(scene_entity_id='test_id', requested_scene=scene)

        Adapter.retrieve(bundle)

        mockUnameNode.assert_called_once()
        assert(bundle.hostname=='testhostname')
        mockSave.assert_called_once()
        mockIsFile.assert_called_once_with('tmp/test_id.tar.gz')
        mockRetrieve.assert_called_once_with('https://example.org', 'tmp/test_id.tar.gz')
        mockExtract.assert_called_once_with('tmp/test_id.tar.gz', bundle.local_path)

    def test_remap_pixel(self):
        assert(Adapter.remap_pixel(0)==2)
        remap = Adapter.remap_pixel(np.array([-9999, 0, 5000, 10000, 20000]))
        assert(remap.tolist()==[0, 2, 127, 252, 255])
        assert(remap.dtype==np.uint8)
