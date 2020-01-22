from django.contrib import admin  # noqa: F401

# Register your models here.

from .models import *

admin.site.register(Project)
admin.site.register(Pipeline)
admin.site.register(PipelineStage)
admin.site.register(JobBundle)
admin.site.register(RequestedScene)
admin.site.register(ImageryRequest)
