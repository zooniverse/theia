from theia.api.models import Project, Pipeline, ImageryRequest
from rest_framework import viewsets
from theia.api.serializers import ProjectSerializer, PipelineSerializer, ImageryRequestSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer


class ImageryRequestViewSet(viewsets.ModelViewSet):
    queryset = ImageryRequest.objects.all()
    serializer_class = ImageryRequestSerializer
