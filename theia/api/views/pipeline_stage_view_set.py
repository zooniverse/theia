from theia.api.models import PipelineStage
from rest_framework import viewsets
from theia.api.serializers import PipelineStageSerializer


class PipelineStageViewSet(viewsets.ModelViewSet):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
