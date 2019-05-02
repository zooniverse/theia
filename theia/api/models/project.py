from django.db import models as models


class Project(models.Model):
    id = models.IntegerField(primary_key=True, null=False)
    name = models.CharField(max_length=128, null=False)

    def __str__(self):
        return self.name
