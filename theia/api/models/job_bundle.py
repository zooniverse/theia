from django.db import models as models
from django.db.models.signals import post_save
from theia.tasks import process_bundle

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

    subject_set_id = models.IntegerField(null=True)

    objects = JobBundleManager()

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            process_bundle.delay(instance.id)

    def __str__(self):
        return '[JobBundle %s on %s]' % (self.scene_entity_id, self.hostname)


post_save.connect(JobBundle.post_save, sender=JobBundle)
