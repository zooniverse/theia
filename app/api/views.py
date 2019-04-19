# from django.shortcuts import render
from django.contrib.auth.models import User, Group
from api.models import ImageryRequest
from rest_framework import viewsets
from api.serializers import UserSerializer, GroupSerializer, ImageryRequestSerializer

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ImageryRequestViewSet(viewsets.ModelViewSet):
    queryset = ImageryRequest.objects.all()
    serializer_class = ImageryRequestSerializer