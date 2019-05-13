from celery import shared_task
from theia.api import models
from .espa_wrapper import EspaWrapper

from datetime import datetime, timedelta
from django.utils.timezone import make_aware


@shared_task(name='theia.adapters.usgs.tasks.wait_for_scene')
def wait_for_scene(requested_scene_id):
    request = models.RequestedScene.objects.get(pk=requested_scene_id)
    if request.status == 1:
        return

    status = EspaWrapper.order_status(request.scene_order_id)
    now = make_aware(datetime.utcnow())
    request.checked_at = now
    request.save()

    if status == 'complete':
        request.status = 1
        request.scene_url = EspaWrapper.download_urls(request.scene_order_id)[0]
        request.save()
        models.JobBundle.objects.from_requested_scene(request)
    else:
        soon = now + timedelta(minutes=15)
        wait_for_scene.apply_async((requested_scene_id,), eta=soon)
