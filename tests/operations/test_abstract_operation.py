import pytest
from unittest import TestCase
from unittest.mock import patch
from theia.operations import AbstractOperation
from theia.api import models
from theia.adapters.dummy import Adapter

# can't instantiate abstractoperation to test, so make a simple
# implementation of the abstract methods
class ConcreteOperation(AbstractOperation):
    def apply(self, filenames):
        return 'not implemented'

class TestAbstractOperation(TestCase):
    def test_init(self):
        bundle = models.JobBundle()
        operation = ConcreteOperation(bundle)

        assert(operation.bundle==bundle)

    def test_imagery_request(self):
        request = models.ImageryRequest(adapter_name='dummy', dataset_name='bar')
        bundle = models.JobBundle(imagery_request=request)
        operation = ConcreteOperation(bundle)

        assert(operation.imagery_request==request)
        assert(operation.adapter_name=='dummy')
        assert(operation.dataset_name=='bar')
        self.assertIsInstance(operation.adapter, Adapter)

    def test_pipeline_stage(self):
        stage = models.PipelineStage(
            output_format='jpg',
            select_images=['a', 'b'],
            config={'foo': 'bar'},
            sort_order=7,
        )
        bundle = models.JobBundle(current_stage=stage)
        operation = ConcreteOperation(bundle)

        assert(operation.pipeline_stage==stage)
        assert(operation.output_extension=='jpg')
        assert(operation.select_images==['a', 'b'])
        assert(operation.config=={'foo': 'bar'})
        assert(operation.sort_order==7)

    def test_get_new_version_simple(self):
        stage = models.PipelineStage(sort_order=2)
        bundle = models.JobBundle(current_stage=stage)
        operation = ConcreteOperation(bundle)
        assert(operation.get_new_version('foo.bar')=='foo_stage_02.bar')

    def test_get_new_version_extension(self):
        stage = models.PipelineStage(sort_order=2, output_format='png')
        bundle = models.JobBundle(current_stage=stage)
        operation = ConcreteOperation(bundle)
        assert(operation.get_new_version('foo.bar')=='foo_stage_02.png')

    @patch('theia.adapters.dummy.Adapter.construct_filename', return_value='dummy filename')
    @patch('theia.utils.FileUtils.absolutize', return_value='absolute name')
    @patch('theia.operations.AbstractOperation.get_new_version', return_value='new version name')
    def test_get_new_filename(self, mock_get_new_version, mock_absolute, mock_construct):
        request = models.ImageryRequest(adapter_name='dummy')
        stage = models.PipelineStage(sort_order=3, output_format='png')
        bundle = models.JobBundle(current_stage=stage, imagery_request=request)
        operation = ConcreteOperation(bundle)

        assert(operation.get_new_filename('some filename')=='new version name')
        mock_construct.assert_called_once_with(bundle, 'some filename')
        mock_absolute.assert_called_once_with(bundle=bundle, filename='dummy filename')
        mock_get_new_version.assert_called_once_with('absolute name')
