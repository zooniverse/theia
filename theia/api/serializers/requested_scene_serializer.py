from theia.api.models import RequestedScene
from rest_framework import serializers


class RequestedSceneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RequestedScene
        fields = '__all__'
