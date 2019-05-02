from theia.api.models import JobBundle
from rest_framework import serializers


class JobBundleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobBundle
        fields = '__all__'
