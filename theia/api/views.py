from theia.api.models import ImageryRequest
from rest_framework import viewsets
from theia.api.serializers import ImageryRequestSerializer

class ImageryRequestViewSet(viewsets.ModelViewSet):
    queryset = ImageryRequest.objects.all()
    serializer_class = ImageryRequestSerializer
