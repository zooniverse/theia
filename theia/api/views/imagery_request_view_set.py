from theia.api.models import ImageryRequest
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from panoptes_client import Panoptes, Project
from panoptes_client.panoptes import PanoptesAPIException

from theia.utils.panoptes_utils import PanoptesUtils
from theia.api.serializers import ImageryRequestSerializer


class ImageryRequestViewSet(viewsets.ModelViewSet):
    queryset = ImageryRequest.objects.all()
    serializer_class = ImageryRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with get_authenticated_panoptes(
                request.session['bearer_token'],
                request.session['bearer_expiry']):
            try:
                Project.find(_id_for(request.data['project']))
                self.perform_create(serializer)

                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except PanoptesAPIException:
                return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED, headers=headers)


def get_authenticated_panoptes(bearer_token, bearer_expiry):
    guest_authenticated_panoptes = Panoptes(
        endpoint=PanoptesUtils.base_url()
    )

    guest_authenticated_panoptes.bearer_token = bearer_token
    guest_authenticated_panoptes.logged_in = True
    bearer_expiry = datetime.strptime(bearer_expiry, "%Y-%m-%d %H:%M:%S.%f")
    guest_authenticated_panoptes.bearer_expires = (bearer_expiry)

    return guest_authenticated_panoptes


def _id_for(project_url):
    components = list(filter(lambda x: x != '', str.split(project_url, "/")))
    return components[len(components) - 1]
