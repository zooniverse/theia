from django.contrib.auth.models import User, Group
from api.models import ImageryRequest
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ImageryRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ImageryRequest
        fields = '__all__'
