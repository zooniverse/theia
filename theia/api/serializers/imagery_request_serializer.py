from theia.api.models import ImageryRequest
from rest_framework_json_api import serializers


class ImageryRequestSerializer(serializers.HyperlinkedModelSerializer):
    requested_scenes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    job_bundles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ImageryRequest
        fields = '__all__'
