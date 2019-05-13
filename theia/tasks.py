from __future__ import absolute_import

import theia.api.models as models
import theia.api.utils as utils
import theia.adapters as adapters

from celery import shared_task
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

@shared_task(name='theia.tasks.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    search = utils.ImagerySearch.build_search(request)
    scenes = adapters.usgs.ErosWrapper.search(search)
    for scene in scenes:
        result = adapters.usgs.EspaWrapper.order_all(scene, 'sr')
        for item in result:
            req = models.RequestedScene(**{**item, **{'imagery_request': request}})
            req.save()


@shared_task(name='theia.tasks.wait_for_scene')
def wait_for_scene(requested_scene_id):
    request = models.RequestedScene.objects.get(pk=requested_scene_id)
    if request.status == 1:
        return

    status = adapters.usgs.EspaWrapper.order_status(request.scene_order_id)
    request.checked_at = make_aware(datetime.utcnow())

    if status == 'complete':
        request.status = 1
        request.scene_url = adapters.usgs.EspaWrapper.download_urls(request.scene_order_id)[0]
        request.save()
        return models.JobBundle.objects.from_requested_scene(request)
    else:
        soon = datetime.utcnow() + timedelta(minutes=15)
        wait_for_scene.apply_async((requested_scene_id,), eta=soon)
        return request.save()


@shared_task(name='theia.tasks.process_bundle')
def process_bundle(job_bundle_id):
    bundle = models.JobBundle.objects.get(pk=job_bundle_id)
    bundle.retrieve()
    target_filename = adapters.usgs.Adapter.resolve_image(bundle.scene_entity_id, bundle.requested_scene.imagery_request.dataset_name, 'aerosol')
    print(target_filename)
    return
