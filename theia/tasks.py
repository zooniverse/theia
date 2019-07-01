from __future__ import absolute_import

from celery import shared_task
from os.path import abspath, join
import glob

import theia.api.models as models
from theia.adapters import adapters
from theia.operations import operations
from theia.utils import FileUtils


@shared_task(name='theia.tasks.locate_scenes')
def locate_scenes(imagery_request_id):
    request = models.ImageryRequest.objects.get(pk=imagery_request_id)
    adapter = adapters[request.adapter_name]()
    adapter.process_request(request)


@shared_task(name='theia.tasks.process_bundle')
def process_bundle(job_bundle_id):
    bundle = models.JobBundle.objects.get(pk=job_bundle_id)
    request = bundle.imagery_request
    pipeline = bundle.pipeline

    adapter = adapters[request.adapter_name]()
    adapter.retrieve(bundle)

    for stage in pipeline.get_stages():
        bundle.current_stage = stage
        bundle.save()

        images = stage.select_images or []
        resolved_names = [_resolve_name(adapter, stage, bundle, name) for name in images]
        flattened_names = [item for sublist in resolved_names for item in sublist]
        operation = operations[stage.operation](bundle)
        operation.apply(flattened_names)


def _resolve_name(adapter, stage, bundle, semantic_name):
    try:
        semantic_name.index('*')
        literal_name = semantic_name
        absolute_filenames = glob.glob(FileUtils.absolutize(bundle=bundle, filename=literal_name))
    except ValueError:
        literal_name = adapter.resolve_relative_image(bundle, semantic_name)
        absolute_filenames = [FileUtils.absolutize(bundle=bundle, filename=literal_name)]

    versioned_filenames = [FileUtils.locate_latest_version(filename, stage.sort_order) for filename in absolute_filenames]
    return versioned_filenames
