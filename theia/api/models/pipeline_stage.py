from django.db import models as models
from django.contrib.postgres.fields import ArrayField
from .pipeline import Pipeline


class PipelineStage(models.Model):
    sort_order = models.IntegerField(null=False)
    output_format = models.CharField(max_length=8, null=True, blank=True)
    operation = models.CharField(max_length=64, null=False)
    select_images = ArrayField(models.CharField(max_length=64, null=False), null=True)
    config = models.JSONField(blank=True)
    pipeline = models.ForeignKey(Pipeline, related_name='pipeline_stages', on_delete=models.CASCADE)

    class Meta:
        ordering = ['pipeline', 'sort_order']

    def __str__(self):
        return self.pipeline.name + ' Stage ' + str(self.sort_order) + ': ' + self.operation

    @property
    def output_filename(self):
        return "%d_%s" % (
            self.sort_order,
            self.operation.replace('.', '_')
        )

    @property
    def interstitial_product_location(self):
        return "%d_%s" % (
            self.sort_order,
            self.operation.replace('.', '_')
        ) + "_interstitial_products"


