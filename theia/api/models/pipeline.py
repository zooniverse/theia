from django.db import models as models
from .project import Project


class Pipeline(models.Model):
    name = models.CharField(max_length=128, null=False)
    workflow_id = models.IntegerField(null=True)

    multiple_subject_sets = models.BooleanField(default=False)
    subject_set_id = models.IntegerField(null=True)

    project = models.ForeignKey(Project, related_name='pipelines', on_delete=models.CASCADE)

    def name_subject_set(self):
        return '%s Pipeline' % (self.name,)

    def get_stages(self):
        return self.pipeline_stages.all()  # pragma: nocover

    def __str__(self):
        return '%s | %s' % (self.project.name, self.name)
