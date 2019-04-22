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
    status = EspaWrapper.order_status(request.scene_order_id)

    request.checked_at = make_aware(datetime.utcnow())

    if status=='completed':
        request.status=1
        print('all done now')
        # schedule download worker
    else:
        soon = datetime.utcnow() + timedelta(minutes=5)
        wait_for_scene.apply_async((requested_scene_id,), eta=soon)

    request.save()

tasks = {
    'locate_scenes': locate_scenes,
    'wait_for_scene': wait_for_scene
}
