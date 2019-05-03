from django.db import models as models
from .project import Project

class Pipeline(models.Model):
    name = models.CharField(max_length=128, null=False)
    associated_workflow_id = models.IntegerField(null=True)
    associated_subject_set_id = models.IntegerField(null=True)
    multiple_subject_sets = models.BooleanField(default=False)
    project = models.ForeignKey(Project, related_name='pipelines', on_delete=models.CASCADE)

    def __str__(self):
        return '%s | %s'  % (self.project.name, self.name)

