from __future__ import absolute_import

import theia.api.models as models
from theia.adapters import adapters
from theia.operations import operations

from celery import shared_task
from os.path import abspath, join


@shared_task(name='theia.tasks.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    adapter = adapters[request.adapter_name]
    adapter.process_request(request)


@shared_task(name='theia.tasks.process_bundle')
def process_bundle(job_bundle_id):
    bundle = models.JobBundle.objects.get(pk=job_bundle_id)
    request = bundle.requested_scene.imagery_request
    stages = request.pipeline.pipeline_stages

    adapter = adapters[request.adapter_name]
    adapter.retrieve(bundle)

    for stage in stages.all():
        for image_name in stage.select_images:
            filename = adapter.resolve_image(bundle, image_name)
            filename = join(abspath(bundle.local_path), filename)
            operations[stage.operation].apply(filename, stage)
