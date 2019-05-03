from theia.api.models import RequestedScene
from rest_framework import serializers


class RequestedSceneSerializer(serializers.HyperlinkedModelSerializer):
    job_bundles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = RequestedScene
        fields = '__all__'
