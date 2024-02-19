from unittest.mock import patch
import theia.adapters.usgs.tasks

EROS_AVAILABLE_PRODUCTS_EXAMPLE = [{'entityId': 'LANDSATIMAGE123', 'productId': 123, 'displayId': 'LANDSAT_IMAGE_123'}]
EROS_REQUEST_DOWNLOAD_PENDING_DOWNLOADS_RESULT = {
    "availableDownloads":[],
    "duplicateProducts":[],
    "preparingDownloads":[
        {
            "downloadId":550754832,
            "eulaCode":"None",
            "url":"https://dds.cr.usgs.gov/download-staging/eyJpZCI6NTUwNzU0ODMyLCJjb250YWN0SWQiOjI2MzY4NDQ1fQ=="
        }
    ]
}

EROS_REQUEST_DOWNLOAD_DOWNLOADS_AVAILABLE_RESULT = {
    "availableDownloads":[{
            "downloadId":550752861,
            "eulaCode":"None",
            "url":"https://dds.cr.usgs.gov/download-staging/eyJpZCI6NTUwNzUyODYxLCJjb250YWN0SWQiOjI2MzY4NDQ1fQ=="
        }],
    "duplicateProducts":[],
    "preparingDownloads":[]
}

@patch('theia.api.models.RequestedScene.objects.get', autospec=True)
@patch('theia.adapters.usgs.ErosWrapper.request_download', autospec=True)
def test_wait_for_scene_already_done(mockStatus, mockGetScene):
    mockGetScene.return_value.status=1
    theia.adapters.usgs.tasks.wait_for_scene(1, EROS_AVAILABLE_PRODUCTS_EXAMPLE)
    mockStatus.assert_not_called()

@patch('theia.api.models.RequestedScene.objects.get', autospec=True)
@patch('theia.adapters.usgs.ErosWrapper.request_download', return_value=EROS_REQUEST_DOWNLOAD_PENDING_DOWNLOADS_RESULT)
@patch('theia.adapters.usgs.tasks.wait_for_scene.apply_async', autospec=True)
def test_wait_for_scene_pending(mockWait, mockStatus, mockGetScene):
    mockGetScene.return_value.status=0
    mockGetScene.return_value.scene_order_id='order id'

    theia.adapters.usgs.tasks.wait_for_scene(3, EROS_AVAILABLE_PRODUCTS_EXAMPLE)

    mockGetScene.assert_called_once_with(pk=3)
    mockStatus.assert_called_once_with(EROS_AVAILABLE_PRODUCTS_EXAMPLE)
    mockGetScene.return_value.save.assert_called_once()
    mockWait.assert_called_once()

@patch('theia.api.models.RequestedScene.objects.get', autospec=True)
@patch('theia.adapters.usgs.ErosWrapper.request_download', return_value=EROS_REQUEST_DOWNLOAD_DOWNLOADS_AVAILABLE_RESULT)
@patch('theia.api.models.JobBundleManager.from_requested_scene', autospec=True)
def test_wait_for_scene_ready(mockConstruct, mockStatus, mockGetScene):
    mockGetScene.return_value.status=0
    mockGetScene.return_value.scene_order_id='order id'
    theia.adapters.usgs.tasks.wait_for_scene(3, EROS_AVAILABLE_PRODUCTS_EXAMPLE)

    mockGetScene.assert_called_once_with(pk=3)
    mockStatus.assert_called_once_with(EROS_AVAILABLE_PRODUCTS_EXAMPLE)
    mockGetScene.return_value.save.assert_called()
    mockConstruct.assert_called_once()