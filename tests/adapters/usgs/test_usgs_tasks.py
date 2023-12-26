import pytest
from unittest.mock import patch
import theia.adapters.usgs.tasks

@patch('theia.api.models.RequestedScene.objects.get', autospec=True)
@patch('theia.adapters.usgs.EspaWrapper.order_status', autospec=True)
def test_wait_for_scene_already_done(mockStatus, mockGetScene):
    mockGetScene.return_value.status=1
    theia.adapters.usgs.tasks.wait_for_scene(1)
    mockStatus.assert_not_called()

@patch('theia.api.models.RequestedScene.objects.get', autospec=True)
@patch('theia.adapters.usgs.EspaWrapper.order_status', return_value='whatever')
@patch('theia.adapters.usgs.EspaWrapper.download_urls', autospec=True)
@patch('theia.adapters.usgs.tasks.wait_for_scene.apply_async', autospec=True)
def test_wait_for_scene_pending(mockWait, mockUrls, mockStatus, mockGetScene):
    mockGetScene.return_value.status=0
    mockGetScene.return_value.scene_order_id='order id'

    theia.adapters.usgs.tasks.wait_for_scene(3)

    mockGetScene.assert_called_once_with(pk=3)
    mockStatus.assert_called_once_with('order id')
    mockGetScene.return_value.save.assert_called_once()
    mockWait.assert_called_once()

@patch('theia.api.models.RequestedScene.objects.get', autospec=True)
@patch('theia.adapters.usgs.EspaWrapper.order_status', return_value='complete')
@patch('theia.adapters.usgs.EspaWrapper.download_urls')
@patch('theia.api.models.JobBundleManager.from_requested_scene', autospec=True)
def test_wait_for_scene_ready(mockConstruct, mockUrls, mockStatus, mockGetScene):
    mockGetScene.return_value.status=0
    mockGetScene.return_value.scene_order_id='order id'
    theia.adapters.usgs.tasks.wait_for_scene(3)

    mockGetScene.assert_called_once_with(pk=3)
    mockStatus.assert_called_once_with('order id')
    mockGetScene.return_value.save.assert_called()
    mockConstruct.assert_called_once()
