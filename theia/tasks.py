from __future__ import absolute_import
from celery import shared_task
from datetime import datetime, timedelta
import theia.api.models as models
import theia.api.utils as utils
from theia.usgs import ErosWrapper, EspaWrapper
from django.utils.timezone import make_aware


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


@shared_task(name='theia.tasks.wait_for_scene')
def wait_for_scene(requested_scene_id):
    request = models.RequestedScene.objects.get(pk=requested_scene_id)
    if request.status == 1:
        return

    status = EspaWrapper.order_status(request.scene_order_id)

    if status=='complete':
        request.status=1
        request.scene_url = EspaWrapper.download_urls(request.scene_order_id)[0]
        process_scene.delay(requested_scene_id)
    else:
        soon = datetime.utcnow() + timedelta(minutes=15)
        wait_for_scene.apply_async((requested_scene_id,), eta=soon)

    request.checked_at = make_aware(datetime.utcnow())
    request.save()


@shared_task(name='theia.tasks.process_scene')
def process_scene(requested_scene_id):
    request = models.RequestedScene.objects.get(pk=requested_scene_id)
    return

tasks = {
    'locate_scenes': locate_scenes,
    'wait_for_scene': wait_for_scene,
    'process_scene': process_scene
}
