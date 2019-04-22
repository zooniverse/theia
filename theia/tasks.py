from __future__ import absolute_import
from celery import shared_task
import theia.api.models as models
import theia.api.utils as utils
from theia.usgs import ErosWrapper, EspaWrapper


@shared_task(name='theia.tasks.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    search = utils.ImagerySearch.build_search(request)
    scenes = ErosWrapper.search(search)
    for scene in scenes:
        result = EspaWrapper.order_all(scene, 'sr')
        for item in result:
            req = models.RequestedScene(**{**item, **{'imagery_request': request}})
            req.save()


@shared_task(name='theia.tasks.acquire_scene')
def acquire_scene(requested_scene_id):
    request = models.RequestedScene.objects.get(pk=requested_scene_id)
    print(request.scene_entity_id)
    return

tasks = {
    'locate_scenes': locate_scenes,
    'acquire_scene': acquire_scene
}
