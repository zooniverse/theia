from __future__ import absolute_import
from celery import shared_task
import theia.api.models as models
import theia.api.utils as utils
from theia.usgs import ErosWrapper, EspaWrapper


@shared_task(name='theia.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    search = utils.ImagerySearch.build_search(request)
    scenes = ErosWrapper.search(search)
    return EspaWrapper.order_all(scenes[0], 'sr')


tasks = {
    'locate_scenes': locate_scenes
}
