import pytest
from unittest.mock import patch, Mock, PropertyMock, call, ANY

import theia.tasks as tasks
from theia.api.models import ImageryRequest, JobBundle, Pipeline, PipelineStage, Project
from theia.adapters.dummy import Adapter


@patch('theia.api.models.ImageryRequest.objects.get', return_value=ImageryRequest(adapter_name='dummy'))
@patch('theia.adapters.dummy.Adapter.process_request')
def test_locate_scenes(mock_process, mock_get):
    tasks.locate_scenes(7)
    mock_get.assert_called_once_with(pk=7)
    mock_process.assert_called_once_with(mock_get.return_value)


@pytest.mark.django_db
@patch('theia.adapters.dummy.Adapter.retrieve')
@patch('theia.operations.noop.NoOp.apply')
@patch('theia.tasks._resolve_name', return_value=['blue_resolved'])
@patch('theia.tasks.images_in_input_directory', return_value=['input_file'])
def test_process_bundle(mock_input_files, mock_resolve, mock_apply, mock_retrieve):
    project = Project(id=4)
    project.save()

    pipeline = Pipeline(project=project)
    pipeline.save()

    stage_1 = PipelineStage(operation='noop', pipeline=pipeline, sort_order=1, config={})
    stage_1.save()

    stage_2 = PipelineStage(operation='noop', select_images=['blue'], pipeline=pipeline, sort_order=2, config={})
    stage_2.save()

    request = ImageryRequest(adapter_name='dummy', pipeline=pipeline, project=project)
    request.save()

    bundle = JobBundle(id=3, total_stages=2)
    bundle.imagery_request = request
    bundle.pipeline = pipeline
    bundle.save()

    tasks.process_bundle(3)

    assert (mock_apply.call_count == 2)
    second_method_call = mock_apply.call_args_list[1]
    arguments = second_method_call[0]
    file_list = arguments[0]
    assert str.endswith(file_list[0], '/theia/1_noop/input_file')

    mock_retrieve.assert_called_once()

@patch('glob.glob', return_value=['/tmp/literal name'])
@patch('theia.utils.FileUtils.locate_latest_version', return_value='versioned name')
@patch('theia.adapters.dummy.Adapter.resolve_relative_image', return_value='literal name')
def test__resolve_name(mock_resolve, mock_locate, mock_glob):
    stage = PipelineStage(select_images=['infrared'], operation='noop', sort_order=5)
    bundle = JobBundle(local_path='/tmp')
    adapter = Adapter

    tasks._resolve_name(adapter=adapter, stage=stage, bundle=bundle, input_directory=None, semantic_name='infrared')
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

    tasks._resolve_name(adapter=adapter, stage=stage, bundle=bundle, input_directory=None, semantic_name='tiles/*.jpg')
    mock_resolve.assert_not_called()
    mock_absolute.assert_called_once_with(bundle=bundle, input_dir=None, filename='tiles/*.jpg')
    mock_glob.assert_called_once_with('tmp/tiles/*.jpg')
    mock_locate.assert_has_calls([
        call('/tmp/literal name', 5),
        call('/tmp/another.jpg', 5),
    ])
