from theia.api.models import Project
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()  # must be editable, not auto-increment
    imagery_requests = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    pipelines = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
