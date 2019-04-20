from __future__ import absolute_import
from celery import shared_task
import theia.api.models as models
from theia.usgs import ErosWrapper

@shared_task(name='theia.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    search = models.ImagerySearch.build_search(request)
    return ErosWrapper.search(search)

tasks = {
    'locate_scenes': locate_scenes
}
