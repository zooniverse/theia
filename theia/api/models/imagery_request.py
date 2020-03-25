from django.db import models as models
from django.db.models.signals import post_save
from datetime import datetime

import theia.tasks
from .project import Project
from .pipeline import Pipeline


class ImageryRequest(models.Model):
    adapter_name = models.CharField(max_length=64, null=False)
    dataset_name = models.CharField(max_length=64, null=False)

    max_cloud_cover = models.IntegerField(null=True)
    begin_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    max_results = models.IntegerField(null=True)

    wgs_row = models.IntegerField(null=True)
    wgs_path = models.IntegerField(null=True)

    kml_polygon = models.TextField(null=True, blank=True)
    bounding_left = models.FloatField(null=True, blank=True)
    bounding_right = models.FloatField(null=True, blank=True)
    bounding_top = models.FloatField(null=True, blank=True)
    bounding_bottom = models.FloatField(null=True, blank=True)

    user_id = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(db_index=True, default=0, blank=True)

    created_at = models.DateTimeField(null=False, auto_now_add=True, db_index=True, blank=True)

    project = models.ForeignKey(Project, related_name='imagery_requests', on_delete=models.CASCADE)
    pipeline = models.ForeignKey(Pipeline, related_name='imagery_requests', on_delete=models.CASCADE)

    def __str__(self):
        when = self.created_at or datetime.utcnow()
        return '[ImageryRequest project %d at %s]' % (self.project_id, when.strftime('%F'))

    @classmethod
    def post_save(cls, sender, instance, created, *args, **kwargs):
        if created:
            # queue up a worker to search for matching scenes
            theia.tasks.locate_scenes.delay(instance.id)


post_save.connect(ImageryRequest.post_save, sender=ImageryRequest)
