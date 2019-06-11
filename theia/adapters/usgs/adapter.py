import os.path
import platform
import urllib.request
import numpy as np

from theia.api import models
from theia.utils import FileUtils

from .imagery_search import ImagerySearch
from .eros_wrapper import ErosWrapper
from .espa_wrapper import EspaWrapper
from .tasks import wait_for_scene


class Adapter:
    @classmethod
    def enum_datasets(cls):
        pass

    @classmethod
    def process_request(cls, imagery_request):
        search = ImagerySearch.build_search(imagery_request)
        scenes = ErosWrapper.search(search)
        for scene in scenes[0:3]:
            result = EspaWrapper.order_all(scene, 'sr')
            for item in result:
                req = models.RequestedScene.objects.create(**{**item, **{'imagery_request': imagery_request}})
                wait_for_scene.delay(req.id)

    @classmethod
    def resolve_image(cls, bundle, semantic_image_name):
        return '%s_sr_%s.tif' % (bundle.scene_entity_id, semantic_image_name)

    @classmethod
    def retrieve(cls, job_bundle):
        if not job_bundle.local_path or not os.path.isdir(job_bundle.local_path):
            # configure bundle with information about who is processing it where
            job_bundle.local_path = 'tmp/%s' % (job_bundle.scene_entity_id,)
            zip_path = '%s.tar.gz' % (job_bundle.local_path,)
            job_bundle.hostname = platform.uname().node
            job_bundle.save()

            # get the compressed scene data if we don't have it
            if not os.path.isfile(zip_path):
                urllib.request.urlretrieve(job_bundle.requested_scene.scene_url, zip_path)

            FileUtils.untar(zip_path, job_bundle.local_path)

    @classmethod
    def acquire_image(cls, imagery_request):
        pass

    @classmethod
    def remap_pixel(cls, x):
        # https://www.usgs.gov/media/files/landsat-8-surface-reflectance-code-lasrc-product-guide
        # remap all valid pixels to 2-252
        # remap out-of-range low pixels to 0
        # remap saturated pixels to 255
        # use np.where and ufuncs to autovectorize
        # return ndarray of dtype uint8
        return np.where((x >= 0) & (x <= 10000),                # noqa: E126, E128
                    np.add(2, np.floor_divide(x * 250, 10000),  # noqa: E126, E128
                        casting='unsafe',                       # noqa: E126, E128
                        dtype=np.uint8),                        # noqa: E126, E128
                np.where((x < 0),                               # noqa: E126, E128
                    np.uint8(0),                                # noqa: E126, E128
                    np.uint8(255)                               # noqa: E126, E128
            ))
