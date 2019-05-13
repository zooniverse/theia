from __future__ import absolute_import

import theia.api.models as models
from theia.adapters import adapters

from celery import shared_task


@shared_task(name='theia.tasks.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    adapter = adapters[request.adapter_name]
    adapter.process_request(request)


@shared_task(name='theia.tasks.process_bundle')
def process_bundle(job_bundle_id):
    bundle = models.JobBundle.objects.get(pk=job_bundle_id)
    request = bundle.requested_scene.imagery_request
    adapter = adapters[request.adapter_name]

    bundle.retrieve()
    target_filename = adapter.resolve_image(bundle.scene_entity_id, bundle.requested_scene.imagery_request.dataset_name, 'aerosol')
    print(target_filename)
    return
