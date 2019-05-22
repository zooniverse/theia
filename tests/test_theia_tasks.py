import pytest
from unittest.mock import patch, Mock, PropertyMock

import theia.tasks as tasks
from theia.api.models import ImageryRequest, JobBundle, Pipeline, PipelineStage, Project
from theia.adapters.dummy import Adapter

@patch('theia.api.models.ImageryRequest.objects.get', return_value=ImageryRequest(adapter_name='dummy'))
@patch('theia.adapters.dummy.Adapter.process_request')
def test_locate_scenes(mockProcess, mockGet):
    tasks.locate_scenes(7)
    mockGet.assert_called_once_with(pk=7)
    mockProcess.assert_called_once_with(mockGet.return_value)

@pytest.mark.focus
@patch('theia.adapters.dummy.Adapter.retrieve')
@patch('theia.tasks._process_stage')
@patch('theia.api.models.JobBundle.objects.get', return_value=JobBundle(id=3))
def test_process_bundle(mockGet, mockProcess, mockRetrieve):
    project = Project()
    pipeline = Pipeline(project=project)
    stage_1 = PipelineStage(operation='noop')
    stage_2 = PipelineStage(operation='noop')
    request = ImageryRequest(adapter_name='dummy', pipeline=pipeline)

    with patch('theia.api.models.Pipeline.get_stages', return_value=[stage_1, stage_2]) as mockStages:
      bundle = mockGet.return_value
      bundle.imagery_request = request
      bundle.pipeline = pipeline

      tasks.process_bundle(3)

      assert(mockProcess.call_count==2)
      mockProcess.assert_called_with(stage_2, bundle, Adapter)
      mockRetrieve.assert_called_once()

@patch('theia.utils.FileUtils.locate_latest_version', return_value='versioned name')
@patch('theia.adapters.dummy.Adapter.resolve_image', return_value='literal name')
@patch('theia.operations.NoOp.apply')
@patch('theia.api.models.JobBundle.save')
def test__process_stage(mockSave, mockApply, mockResolve, mockLocate):
    stage = PipelineStage(select_images=['infrared'], operation='noop', sort_order=5)
    bundle = JobBundle(local_path='/tmp')
    adapter = Adapter

    tasks._process_stage(stage, bundle, adapter)
    mockResolve.assert_called_once_with(bundle, 'infrared')
    mockLocate.assert_called_once_with('/tmp/literal name', 5)
    mockApply.assert_called_once_with('versioned name', bundle)
