from theia.api.models import ImageryRequest
from rest_framework import serializers


class ImageryRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImageryRequest
        fields = '__all__'
