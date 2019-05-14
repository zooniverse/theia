from theia.api.models import PipelineStage
from rest_framework import serializers


class PipelineStageSerializer(serializers.HyperlinkedModelSerializer):
    job_bundles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = PipelineStage
        fields = '__all__'
