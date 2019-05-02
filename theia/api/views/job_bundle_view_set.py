from theia.api.models import JobBundle
from rest_framework import viewsets
from theia.api.serializers import JobBundleSerializer


class JobBundleViewSet(viewsets.ModelViewSet):
    queryset = JobBundle.objects.all()
    serializer_class = JobBundleSerializer
