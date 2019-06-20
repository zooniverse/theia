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

    def test_resolve_relative_image(self):
        request = ImageryRequest(adapter_name='usgs', dataset_name='LANDSAT_8_C1')
        bundle = JobBundle(scene_entity_id='LC08', imagery_request=request, local_path='tmp/')
        assert(Adapter.resolve_relative_image(bundle, 'red') == 'LC08_sr_band4.tif')

    def test_construct_filename(self):
        bundle = JobBundle(scene_entity_id='LC08', local_path='tmp/')
        assert(Adapter.construct_filename(bundle, 'aerosol')=='LC08_sr_aerosol.tif')

    @patch('theia.adapters.usgs.ImagerySearch.build_search', return_value={})
    @patch('theia.adapters.usgs.ErosWrapper.search', return_value=['some scene id'])
    @patch('theia.adapters.usgs.EspaWrapper.order_all', return_value=[{}])
    @patch('theia.api.models.RequestedScene.objects.create', return_value=RequestedScene(id=3))
    @patch('theia.adapters.usgs.tasks.wait_for_scene.delay')
    def test_process_request(self, mock_wait, mock_rso, mock_order_all, mock_search, mock_build):
        request = ImageryRequest()
        Adapter.process_request(request)

        mock_build.assert_called_once_with(request)
        mock_search.assert_called_once_with({})
        mock_order_all.assert_called_once_with('some scene id', 'sr')
        mock_rso.assert_called_once()
        mock_wait.assert_called_once_with(3)

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
        assert(Adapter.remap_pixel(0)==0)
        remap = Adapter.remap_pixel(np.array([-9999, 0, 5000, 10000, 20000]))
        assert(remap.tolist()==[0, 0, 125, 250, 255])
        assert(remap.dtype==np.uint8)

    @patch('theia.adapters.usgs.ImagerySearch.build_search', return_value={})
    @patch('theia.adapters.usgs.ErosWrapper.search', return_value=[1, 2, 3, 4, 5])
    @patch('theia.adapters.usgs.EspaWrapper.order_all', return_value=[{}])
    @patch('theia.api.models.RequestedScene.objects.create', return_value=RequestedScene(id=3))
    @patch('theia.adapters.usgs.tasks.wait_for_scene.delay')
    def test_limit_scenes(self, mock_wait, mock_rso, mock_order_all, mock_search, mock_build):
        request = ImageryRequest(max_results=3)
        Adapter.process_request(request)

        assert(mock_order_all.call_count==3)

