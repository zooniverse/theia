"""theia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers
from theia.api import views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

router = routers.DefaultRouter()
router.register(r'imagery_requests', views.ImageryRequestViewSet)
router.register(r'job_bundles', views.JobBundleViewSet)
router.register(r'pipelines', views.PipelineViewSet)
router.register(r'pipeline_stages', views.PipelineStageViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'requested_scenes', views.RequestedSceneViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),

    url(r'^$', views.home, name='home'),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'oauth/', include('social_django.urls', namespace='social')),
    url(r'^login$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout$', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
