from theia.api.models import Pipeline
from rest_framework import serializers


class PipelineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pipeline
        fields = '__all__'
