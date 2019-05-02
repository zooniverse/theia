from theia.api.models import Pipeline
from rest_framework import viewsets
from theia.api.serializers import PipelineSerializer


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
