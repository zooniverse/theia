import pytest
from unittest.mock import patch, Mock, PropertyMock

from theia.api.models import JobBundle, Pipeline, Project
from theia.operations.panoptes_operations import UploadSubject
from panoptes_client import Subject, SubjectSet

# some of the tests here are weird because writing tests for the python api client
# is really difficult
# the panoptes api client intercepts property accesses and so is hard to mock
class TestUploadSubject:
    @patch('theia.api.models.Pipeline.name_subject_set', return_value='pipeline name')
    @patch('theia.operations.panoptes_operations.UploadSubject._connect')
    @patch('theia.operations.panoptes_operations.UploadSubject._get_subject_set', return_value=SubjectSet())
    @patch('theia.operations.panoptes_operations.UploadSubject._create_subject', return_value=Subject())
    @patch('panoptes_client.SubjectSet.add')
    def test_apply_single(self, mockAdd, mockCreate, mockGet, mockConnect, mockGetName, *args):
        project = Project(id=8)
        pipeline = Pipeline(project=project)
        bundle = JobBundle(pipeline=pipeline)

        operation = UploadSubject(bundle)
        operation.apply(['some_file'])

        mockConnect.assert_called_once()
        mockGetName.assert_called_once()
        mockGet.assert_called_once_with(pipeline, 8, 'pipeline name')
        mockCreate.assert_called_once_with(8, 'some_file')
        mockAdd.assert_called_once_with(mockCreate.return_value)

    @patch('theia.api.models.JobBundle.name_subject_set', return_value='bundle name')
    @patch('theia.operations.panoptes_operations.UploadSubject._connect')
    @patch('theia.operations.panoptes_operations.UploadSubject._get_subject_set', return_value=SubjectSet())
    @patch('theia.operations.panoptes_operations.UploadSubject._create_subject', return_value=Subject())
    @patch('panoptes_client.SubjectSet.add')
    def test_apply_multiple(self, mockAdd, mockCreate, mockGet, mockConnect, mockGetName, *args):
        project = Project(id=8)
        pipeline = Pipeline(project=project, multiple_subject_sets=True)
        bundle = JobBundle(pipeline=pipeline)

        operation = UploadSubject(bundle)
        operation.apply(['some_file'])

        mockConnect.assert_called_once()
        mockGetName.assert_called_once()
        mockGet.assert_called_once_with(bundle, 8, 'bundle name')
        mockCreate.assert_called_once_with(8, 'some_file')
        mockAdd.assert_called_once_with(mockCreate.return_value)

    @patch('panoptes_client.Panoptes.connect')
    @patch('theia.utils.PanoptesUtils.base_url', return_value='sample url')
    @patch('theia.utils.PanoptesUtils.client_id', return_value='sample id')
    @patch('theia.utils.PanoptesUtils.client_secret', return_value='sample secret')
    def test__connect(self, mockSecret, mockId, mockUrl, mockConnect):
        operation = UploadSubject(JobBundle())
        operation._connect()
        mockUrl.assert_called_once()
        mockId.assert_called_once()
        mockSecret.assert_called_once()
        mockConnect.assert_called_once_with(endpoint='sample url', client_id='sample id', client_secret='sample secret')

    @patch('theia.api.models.JobBundle.save')
    @patch('theia.api.models.Pipeline.save')
    @patch('theia.operations.panoptes_operations.UploadSubject._create_subject_set')
    @patch('panoptes_client.SubjectSet.find', autospec=True)
    def test__get_subject_set(self, mockFind, mockCreateSet, *args):
        mockFind.reset_mock()
        mockCreateSet.reset_mock()

        emptyJobBundle = JobBundle()
        linkedJobBundle = JobBundle(subject_set_id=3)
        emptyPipeline = Pipeline()
        linkedPipeline = Pipeline(subject_set_id=3)

        operation = UploadSubject(emptyJobBundle)
        result = operation._get_subject_set(emptyJobBundle, 8, 'some name')
        mockFind.assert_not_called()
        mockCreateSet.assert_called_once_with(8, 'some name')

        mockFind.reset_mock()
        mockCreateSet.reset_mock()

        operation = UploadSubject(linkedJobBundle)
        result = operation._get_subject_set(linkedJobBundle, 8, 'some name')
        mockFind.assert_called_once_with(3)
        mockCreateSet.assert_not_called()

        mockFind.reset_mock()
        mockCreateSet.reset_mock()

        operation = UploadSubject(emptyPipeline)
        result = operation._get_subject_set(emptyPipeline, 8, 'some name')
        mockFind.assert_not_called()
        mockCreateSet.assert_called_once_with(8, 'some name')

        mockFind.reset_mock()
        mockCreateSet.reset_mock()

        operation = UploadSubject(linkedPipeline)
        result = operation._get_subject_set(linkedPipeline, 8, 'some name')
        mockFind.assert_called_once_with(3)
        mockCreateSet.assert_not_called()

    @patch('panoptes_client.Project.find', return_value=Mock())
    @patch('panoptes_client.Subject.save', autospec=True)
    @patch('panoptes_client.Subject.add_location', autospec=True)
    def test__create_subject_no_metadata(self, mockAdd, mockSave, mockFind):
        operation = UploadSubject(None)
        created_subject = operation._create_subject(1, 'some_file')
        mockFind.assert_called_once_with(1)
        mockAdd.assert_called_once_with(created_subject, 'some_file')  # weird
        mockSave.assert_called_once()
        assert(mockFind.return_value==created_subject.links.project.id)  # weird

    @patch('panoptes_client.Project.find', return_value=Mock())
    @patch('panoptes_client.Subject.save', autospec=True)
    @patch('panoptes_client.Subject.add_location', autospec=True)
    def test__create_subject_with_metadata(self, mockAdd, mockSave, mockFind):
        operation = UploadSubject(None)
        created_subject = operation._create_subject(1, 'some_file', {'foo': 'bar'})
        mockFind.assert_called_once_with(1)
        mockAdd.assert_called_once_with(created_subject, 'some_file')  # weird
        mockSave.assert_called_once()
        assert(mockFind.return_value==created_subject.links.project.id)  # weird
        assert(created_subject.metadata=={'foo': 'bar'})

    @patch('panoptes_client.Project.find', return_value=Mock())
    @patch('panoptes_client.SubjectSet.save', autospec=True)
    def test__create_subject_set(self, mockSave, mockFind):
        operation = UploadSubject(None)
        created_set = operation._create_subject_set(1, 'some name')

        mockFind.assert_called_once_with(1)
        mockSave.assert_called_once()
        assert(created_set.display_name=='some name')
        assert(mockFind.return_value==created_set.links.project.id)  # weird
