from django.db import models as models
from django.db.models.signals import post_save
from theia.tasks import tasks


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
    project_id = models.IntegerField(db_index=True)
    multiple_subject_sets = models.BooleanField(default=False)
    status = models.IntegerField(db_index=True, default=0)
    pending_downloads = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=False, auto_now_add=True, db_index=True)

    def __str__(self):
        return '[ImageryRequest project %d at %s]' % (self.project_id, self.created_at.strftime('%F'))

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if created:
            # queue up a worker to search for matching scenes
            tasks['locate_scenes'].delay(instance.id)


post_save.connect(ImageryRequest.post_create, sender=ImageryRequest)


class RequestedScene(models.Model):
    scene_entity_id = models.CharField(max_length=64, null=False)
    scene_order_id = models.CharField(max_length=128, null=False)
    scene_url = models.CharField(max_length=512)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=False)
    checked_at = models.DateTimeField(db_index=True, null=True)
    imagery_request = models.ForeignKey(ImageryRequest, on_delete=models.CASCADE)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if created:
            tasks['wait_for_scene'].delay(instance.id)

    def __str__(self):
        return '[RequestedScene %s status %i]' % (self.scene_entity_id, self.status)


post_save.connect(RequestedScene.post_create, sender=RequestedScene)