from theia.api.models import RequestedScene
from rest_framework import viewsets
from theia.api.serializers import RequestedSceneSerializer


class RequestedSceneViewSet(viewsets.ModelViewSet):
    queryset = RequestedScene.objects.all()
    serializer_class = RequestedSceneSerializer
