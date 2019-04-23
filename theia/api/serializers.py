from theia.api.models import Project, Pipeline, ImageryRequest
from rest_framework import serializers


class ImageryRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImageryRequest
        fields = '__all__'


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']


class PipelineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pipeline
        fields = '__all__'