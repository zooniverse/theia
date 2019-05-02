from django.db import models as models
from django.db.models.signals import post_save
from theia.tasks import tasks
from django.contrib.postgres.fields import JSONField


class Project(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=128, null=False)

    def __str__(self):
        return self.name


class Pipeline(models.Model):
    name = models.CharField(max_length=128, null=False)
    associated_workflow_id = models.IntegerField(null=True)
    associated_subject_set_id = models.IntegerField(null=True)
    multiple_subject_sets = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return '%s | %s'  % (self.project.name, self.name)


class PipelineStage(models.Model):
    sort_order = models.IntegerField(null=False)
    operation = models.CharField(max_length=64, null=False)
    config = JSONField()
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)


class ImageryRequest(models.Model):
    dataset_name = models.CharField(max_length=64)

    max_cloud_cover = models.IntegerField(null=True)
    begin_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    wgs_row = models.IntegerField(null=True)
    wgs_path = models.IntegerField(null=True)

    kml_polygon = models.TextField(null=True)
    bounding_left = models.FloatField(null=True)
    bounding_right = models.FloatField(null=True)
    bounding_top = models.FloatField(null=True)
    bounding_bottom = models.FloatField(null=True)

    user_id = models.IntegerField(null=True)

    status = models.IntegerField(db_index=True, default=0)
    created_at = models.DateTimeField(null=False, auto_now_add=True, db_index=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)

    def __str__(self):
        return '[ImageryRequest project %d at %s]' % (self.project_id, self.created_at.strftime('%F'))

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            # queue up a worker to search for matching scenes
            tasks['locate_scenes'].delay(instance.id)


class RequestedScene(models.Model):
    scene_entity_id = models.CharField(max_length=64, null=False)
    scene_order_id = models.CharField(max_length=128, null=False)
    scene_url = models.CharField(max_length=512)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=False)
    checked_at = models.DateTimeField(db_index=True, null=True)
    imagery_request = models.ForeignKey(ImageryRequest, on_delete=models.CASCADE)

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            tasks['wait_for_scene'].delay(instance.id)

    def __str__(self):
        return '[RequestedScene %s status %i]' % (self.scene_entity_id, self.status)


class JobBundle(models.Model):
    imagery_request = models.ForeignKey(ImageryRequest, on_delete=models.SET_NULL, null=True)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE)
    current_stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True)
    requested_scene = models.ForeignKey(RequestedScene, on_delete=models.SET_NULL, null=True)

    scene_entity_id = models.CharField(max_length=64, null=False)
    current_stage_index = models.IntegerField(default=0, null=False)
    total_stages = models.IntegerField(null=False)

    status = models.IntegerField(default=0, null=False)
    hostname = models.CharField(max_length=128, null=False, default='')
    local_path = models.CharField(max_length=512, null=False, default='')
    dir_size = models.IntegerField(default=0, null=False)
    hearbeat = models.DateTimeField(null=True)

    @classmethod
    def from_requested_scene(requested_scene):
        return JobBundle.objects.create(
            imagery_request=requested_scene.imagery_request,
            pipeline=requested_scene.imagery_request.pipeline,
            requested_scene=requested_scene,
            scene_entity_id=requested_scene.scene_entity_id,
            total_stages=requested_scene.imagery_request.pipeline.pipeline_stage_set.count()
        )

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            tasks['process_scene'].delay(instance.id)

    def __str__(self):
        return '[JobBundle %s on %s]' % (self.scene_entity_id, self.hostname)


post_save.connect(ImageryRequest.post_save, sender=ImageryRequest)
post_save.connect(RequestedScene.post_save, sender=RequestedScene)
post_save.connect(JobBundle.post_save, sender=JobBundle)
