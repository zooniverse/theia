from theia.api.models import Pipeline
from rest_framework import serializers


class PipelineSerializer(serializers.HyperlinkedModelSerializer):
    imagery_requests = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    pipeline_stages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    job_bundles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Pipeline
        fields = '__all__'
