import pytest
from unittest.mock import patch, Mock, PropertyMock, call

import theia.tasks as tasks
from theia.api.models import ImageryRequest, JobBundle, Pipeline, PipelineStage, Project
from theia.adapters.dummy import Adapter

@patch('theia.api.models.ImageryRequest.objects.get', return_value=ImageryRequest(adapter_name='dummy'))
@patch('theia.adapters.dummy.Adapter.process_request')
def test_locate_scenes(mock_process, mock_get):
    tasks.locate_scenes(7)
    mock_get.assert_called_once_with(pk=7)
    mock_process.assert_called_once_with(mock_get.return_value)

@patch('theia.adapters.dummy.Adapter.retrieve')
@patch('theia.api.models.JobBundle.objects.get', return_value=JobBundle(id=3))
@patch('theia.api.models.JobBundle.save')
@patch('theia.operations.noop.NoOp.apply')
@patch('theia.tasks._resolve_name', return_value=['blue_resolved'])
def test_process_bundle(mock_resolve, mock_apply, mock_save, mock_get, mock_retrieve):
    project = Project()
    pipeline = Pipeline(project=project)
    stage_1 = PipelineStage(operation='noop')
    stage_2 = PipelineStage(operation='noop', select_images=['blue'])
    request = ImageryRequest(adapter_name='dummy', pipeline=pipeline)

    with patch('theia.api.models.Pipeline.get_stages', return_value=[stage_1, stage_2]) as mockStages:
        bundle = mock_get.return_value
        bundle.imagery_request = request
        bundle.pipeline = pipeline

        tasks.process_bundle(3)

        assert(mock_save.call_count==2)

        assert(mock_apply.call_count==2)
        mock_apply.assert_called_with(['blue_resolved'])

        mock_resolve.assert_called_with(Adapter, stage_2, bundle, 'blue')
        mock_retrieve.assert_called_once()

@patch('glob.glob', return_value=['/tmp/literal name'])
@patch('theia.utils.FileUtils.locate_latest_version', return_value='versioned name')
@patch('theia.adapters.dummy.Adapter.resolve_relative_image', return_value='literal name')
def test__resolve_name(mock_resolve, mock_locate, mock_glob):
    stage = PipelineStage(select_images=['infrared'], operation='noop', sort_order=5)
    bundle = JobBundle(local_path='/tmp')
    adapter = Adapter

    tasks._resolve_name(adapter, stage, bundle, 'infrared')
    mock_resolve.assert_called_once_with(bundle, 'infrared')
    mock_locate.assert_called_once_with('/tmp/literal name', 5)

@patch('glob.glob', return_value=['/tmp/literal name', '/tmp/another.jpg'])
@patch('theia.utils.FileUtils.locate_latest_version', return_value='versioned name')
@patch('theia.utils.FileUtils.absolutize', return_value='tmp/tiles/*.jpg')
@patch('theia.adapters.dummy.Adapter.resolve_relative_image')
def test__resolve_name_wildcard(mock_resolve, mock_absolute, mock_locate, mock_glob):
    stage = PipelineStage(select_images=['infrared'], operation='noop', sort_order=5)
    bundle = JobBundle(local_path='/tmp')
    adapter = Adapter

    tasks._resolve_name(adapter, stage, bundle, 'tiles/*.jpg')
    mock_resolve.assert_not_called()
    mock_absolute.assert_called_once_with(bundle=bundle, filename='tiles/*.jpg')
    mock_glob.assert_called_once_with('tmp/tiles/*.jpg')
    mock_locate.assert_has_calls([
        call('/tmp/literal name', 5),
        call('/tmp/another.jpg', 5),
    ])
