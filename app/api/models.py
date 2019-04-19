from django.db import models
from django.db.models.signals import post_save

# Create your models here.

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
    created_at = models.DateTimeField(null=False, auto_now_add=True, db_index=True)

    def __str__(self):
        return '[ImageryRequest project %d at %s]' % (self.project_id, self.created_at.strftime('%F'))

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        print("post create hook running")
        if not created:
            return
        print("this is where we would create the celery job")

post_save.connect(ImageryRequest.post_create, sender=ImageryRequest)