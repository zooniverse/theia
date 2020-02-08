from theia.api.models import ImageryRequest
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from theia.api.serializers import ImageryRequestSerializer


class ImageryRequestViewSet(viewsets.ModelViewSet):
    queryset = ImageryRequest.objects.all()
    serializer_class = ImageryRequestSerializer

    def create(self, request, *args, **kwargs):
        copy = request.data.copy()
        copy['bearer_token'] = request.session['bearer_token']
        copy['refresh_token'] = request.session['refresh_token']
        copy['bearer_expiry'] = request.session['bearer_expiry']

        serializer = self.get_serializer(data=copy)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)