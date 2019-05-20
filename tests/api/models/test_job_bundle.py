import pytest
from unittest.mock import patch

from django.test import TestCase
import theia.tasks
from theia.api.models import ImageryRequest, JobBundle, JobBundleManager, Pipeline, Project, RequestedScene

class TestJobBundle(TestCase):
    @patch('theia.api.models.JobBundle.objects.create')
    def test_from_requested_scene(self, mockCreate):
        project = Project(id=7)
        pipeline = Pipeline(project=project)
        request = ImageryRequest(pipeline=pipeline, project=project)
        scene = RequestedScene(imagery_request=request, scene_entity_id='entity id')
        bundle = JobBundle.objects.from_requested_scene(scene)

        mockCreate.assert_called_once()
        mockCreate.assert_called_once_with(
            imagery_request=request,
            pipeline = pipeline,
            requested_scene = scene,
            scene_entity_id = 'entity id',
            total_stages=0
        )

    def test_name_subject_set(self):
        bundle = JobBundle(scene_entity_id='entity')
        assert(bundle.name_subject_set() == 'entity')

    def test___str__(self):
        bundle = JobBundle(scene_entity_id='entity', hostname='some.host')
        assert(bundle.__str__()=='[JobBundle entity on some.host]')

        bundle = JobBundle(scene_entity_id='entity')
        assert(bundle.__str__()=='[JobBundle entity on no host]')

    def test_post_create(self):
        '''it enqueues a job after being created'''
        bundle = JobBundle(id=7)
        with patch.object(theia.tasks, 'process_bundle', autospec=True) as mockProcess:
            with patch.object(mockProcess.return_value, 'delay', autospec=True) as mockDelay:
                JobBundle.post_save(None, bundle, False)
                mockDelay.assert_not_called()

                JobBundle.post_save(None, bundle, True)
                mockDelay.assert_called_once_with(bundle.id)
