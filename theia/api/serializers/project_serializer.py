from theia.api.models import Project
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()  # must be editable, not auto-increment
    class Meta:
        model = Project
        fields = '__all__'
