from celery import shared_task
from theia.api import models
# from .espa_wrapper import EspaWrapper
from .eros_wrapper import ErosWrapper

from datetime import datetime, timedelta
from django.utils.timezone import make_aware


@shared_task(name='theia.adapters.usgs.tasks.wait_for_scene')
def wait_for_scene(requested_scene_id, available_products):
    print('MDY114 AVAILABLE PRODUCTS IN WAIT')
    print(available_products)
    request = models.RequestedScene.objects.get(pk=requested_scene_id)
    if request.status == 1:
        return

    # TO DO CHANGES THIS TO REQUEST FROM REQUEST DOWNLOAD
    #status = EspaWrapper.order_status(request.scene_order_id)
    eros_wrapper = ErosWrapper()
    rerequest_download_result = eros_wrapper.request_download(available_products)
    print('MDY114 REREQUEST DOWNLOAD')
    print(rerequest_download_result)
    now = make_aware(datetime.utcnow())
    request.checked_at = now
    request.save()

    if rerequest_download_result['preparingDownloads'] != None and len(rerequest_download_result['preparingDownloads']) == 0:
        request.status = 1
        print('MDY114 BEFORE AVAIL DOWNLOADS CHECK')
        print(rerequest_download_result['availableDownloads'])
        print(len(rerequest_download_result['availableDownloads']))
        if len(rerequest_download_result['availableDownloads']) > 0:
            for item in rerequest_download_result['availableDownloads']:
                print(item)
                request.scene_url = item['url']
        request.save()
        models.JobBundle.objects.from_requested_scene(request)
    else:
        soon = now + timedelta(minutes=5)
        wait_for_scene.apply_async((requested_scene_id,available_products), eta=soon)
