from theia.api.models import PipelineStage
from rest_framework import serializers


class PipelineStageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PipelineStage
        fields = '__all__'
