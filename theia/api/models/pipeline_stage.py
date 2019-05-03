from django.db import models as models
from django.contrib.postgres.fields import JSONField
from .pipeline import Pipeline


class PipelineStage(models.Model):
    sort_order = models.IntegerField(null=False)
    operation = models.CharField(max_length=64, null=False)
    config = JSONField()
    pipeline = models.ForeignKey(Pipeline, related_name='pipeline_stages', on_delete=models.CASCADE)
