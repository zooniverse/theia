from __future__ import absolute_import

import theia.api.models as models
from theia.adapters import adapters
from theia.operations import operations
from theia.utils import FileUtils

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
        bundle.current_stage = stage
        bundle.save()

        for semantic_name in stage.select_images:
            literal_name = adapter.resolve_image(bundle, semantic_name)
            absolute_filename = join(abspath(bundle.local_path), literal_name)
            versioned_filename = FileUtils.locate_latest_version(absolute_filename, stage.sort_order)

            operations[stage.operation].apply(versioned_filename, bundle)
