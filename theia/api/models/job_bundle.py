from django.db import models as models
from django.db.models.signals import post_save
from theia.tasks import process_scene
from urllib.request import urlretrieve

import os.path
import platform
import tarfile

from .imagery_request import ImageryRequest
from .pipeline import Pipeline
from .pipeline_stage import PipelineStage
from .requested_scene import RequestedScene


class JobBundleManager(models.Manager):
    def from_requested_scene(self, requested_scene):
        job_bundle = self.create(
            imagery_request=requested_scene.imagery_request,
            pipeline=requested_scene.imagery_request.pipeline,
            requested_scene=requested_scene,
            scene_entity_id=requested_scene.scene_entity_id,
            total_stages=requested_scene.imagery_request.pipeline.pipeline_stages.count()
        )

        return job_bundle


class JobBundle(models.Model):
    imagery_request = models.ForeignKey(ImageryRequest, related_name='job_bundles', on_delete=models.SET_NULL, null=True)
    pipeline = models.ForeignKey(Pipeline, related_name='job_bundles', on_delete=models.CASCADE)
    current_stage = models.ForeignKey(PipelineStage, related_name='job_bundles', on_delete=models.SET_NULL, null=True)
    requested_scene = models.ForeignKey(RequestedScene, related_name='job_bundles', on_delete=models.SET_NULL, null=True)

    scene_entity_id = models.CharField(max_length=64, null=False)
    current_stage_index = models.IntegerField(default=0, null=False)
    total_stages = models.IntegerField(null=False)

    status = models.IntegerField(default=0, null=False)
    hostname = models.CharField(max_length=128, null=False, default='')
    local_path = models.CharField(max_length=512, null=False, default='')
    dir_size = models.IntegerField(default=0, null=False)
    hearbeat = models.DateTimeField(null=True)

    objects = JobBundleManager()

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            process_scene.delay(instance.id)

    def __str__(self):
        return '[JobBundle %s on %s]' % (self.scene_entity_id, self.hostname)

    def retrieve(self):
        if not self.local_path or not os.path.isdir(self.local_path):
            # configure bundle with information about who is processing it where
            self.local_path = 'tmp/%s' % (self.scene_entity_id,)
            zip_path = '%s.tar.gz' % (self.local_path,)
            self.hostname = platform.uname().node
            self.save()

            # make the temp directory if it doesn't already exist
            if not os.path.isdir(self.local_path):
                os.mkdir(self.local_path)

            # get the compressed scene data if we don't have it
            if not os.path.isfile(zip_path):
                urlretrieve(self.requested_scene.scene_url, zip_path)

            # extract the file
            with tarfile.open(zip_path, 'r') as archive:
                archive.extractall(self.local_path)


post_save.connect(JobBundle.post_save, sender=JobBundle)
