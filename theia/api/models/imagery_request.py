from django.db import models as models
from django.db.models.signals import post_save
from theia.tasks import locate_scenes
from .project import Project
from .pipeline import Pipeline


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

    project = models.ForeignKey(Project, related_name='imagery_requests', on_delete=models.CASCADE)
    pipeline = models.ForeignKey(Pipeline, related_name='imagery_requests', on_delete=models.CASCADE)

    def __str__(self):
        return '[ImageryRequest project %d at %s]' % (self.project_id, self.created_at.strftime('%F'))

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            # queue up a worker to search for matching scenes
            locate_scenes.delay(instance.id)


post_save.connect(ImageryRequest.post_save, sender=ImageryRequest)
