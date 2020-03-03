from __future__ import absolute_import

from celery import shared_task

import glob
import os

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

    for index, stage in enumerate(pipeline.get_stages()):
        input_directory = None

        if index == 0:
            images = stage.select_images or []  # This means the channels. Not sure whether it will ever be something besides channels
            fimenames_array = [_resolve_name(adapter, stage, bundle, input_directory, name) for name in images]
            filename_list = [item for sublist in fimenames_array for item in sublist]
        else:
            input_directory = pipeline.get_stages()[index -1].output_filename
            images = images_in_input_directory(bundle, input_directory)
            filename_list = [os.path.join(os.path.abspath(bundle.local_path), input_directory, name) for name in images]

        bundle.current_stage = stage
        bundle.save()

        operation = operations[stage.operation](bundle)
        operation.apply(filename_list)


def images_in_input_directory(bundle, input_directory):
    return os.listdir(os.path.join(os.path.abspath(bundle.local_path), input_directory))

def _resolve_name(adapter, stage, bundle, input_directory, semantic_name):
    try:
        semantic_name.index('*')
        literal_name = semantic_name
        absolute_filenames = glob.glob(FileUtils.absolutize(bundle=bundle, input_dir=input_directory, filename=literal_name))
    except ValueError:

        literal_name = adapter.resolve_relative_image(bundle, semantic_name)
        absolute_filenames = [FileUtils.absolutize(bundle=bundle, input_dir=input_directory, filename=literal_name)]

    versioned_filenames = [FileUtils.locate_latest_version(filename, stage.sort_order) for filename in absolute_filenames]
    return versioned_filenames
