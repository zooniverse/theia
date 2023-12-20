import os.path
import platform
import re
import urllib.request
import numpy as np

from theia.api import models
from theia.utils import FileUtils

from .eros_wrapper import ErosWrapper
from .espa_wrapper import EspaWrapper
from .imagery_search import ImagerySearch
from .tasks import wait_for_scene
from .xml_helper import XmlHelper


class Adapter:
    DATASET_LOOKUP = {
        'LANDSAT_TM_C1': {
            # LANDSAT 4, LANDSAT 5
            'blue': 'band1',
            'green': 'band2',
            'red': 'band3',
            'nir': 'band4',
            'swir-1': 'band5',
            'swir-2': 'band7',
        },
        'LANDSAT_ETM_C1': {
            # https://www.usgs.gov/media/files/landsat-7-data-users-handbook
            'blue': 'band1',
            'green': 'band2',
            'red': 'band3',
            'nir': 'band4',
            'swir-1': 'band5',
            'swir-2': 'band7',
        },
        'LANDSAT_8_C1': {
            # https://www.usgs.gov/media/files/landsat-8-data-users-handbook
            'coastal_aerosol': 'band1',
            'blue': 'band2',
            'green': 'band3',
            'red': 'band4',
            'nir': 'band5',
            'swir-1': 'band6',
            'swir-2': 'band7',
        },
        'LANDSAT_OT_C2_L1': {
            'coastal_aerosol': 'band1',
            'blue': 'band2',
            'green': 'band3',
            'red': 'band4',
            'nir': 'band5',
            'swir-1': 'band6',
            'swir-2': 'band7',
        },
    }

    def __init__(self):
        self.xml_helper = None

    def process_request(self, imagery_request):
        search = ImagerySearch.build_search(imagery_request)
        print('MDY114 BEFORE EROS WRAPPER')
        scenes = ErosWrapper().search(search)
        print('MDY114 AFTER EROS WRAPPER SCENES')
        print(scenes)
        if imagery_request.max_results:
            scenes = scenes[0:imagery_request.max_results]
            print('MDY114 SCENES')
            print(scenes)

        for scene in scenes:
            print('MDY114 BEFORE ESPA')
            result = EspaWrapper.order_all(scene, 'sr')
            print('MDY114 AFTER ESPA')
            print(result)
            for item in result:
                req = models.RequestedScene.objects.create(**{**item, **{'imagery_request': imagery_request}})
                wait_for_scene.delay(req.id)

    def construct_filename(self, bundle, suffix):
        product = "sr"
        return '%s_%s_%s.%s' % (bundle.scene_entity_id, product, suffix, self.default_extension())

    def resolve_relative_image(self, bundle, semantic_image_name):
        request = bundle.imagery_request
        dataset_name = request.dataset_name

        lookup = self.DATASET_LOOKUP.get(dataset_name, {})
        suffix = lookup.get(semantic_image_name, semantic_image_name)
        product = 'sr'

        return '%s_%s_%s.%s' % (bundle.scene_entity_id, product, suffix, self.default_extension())

    def retrieve(self, job_bundle):
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

    def default_extension(self):
        return 'tif'

    def remap_pixel(self, x):
        # https://www.usgs.gov/media/files/landsat-8-surface-reflectance-code-lasrc-product-guide
        # remap all valid pixels to 2-255
        # remap out-of-range low pixels to 0
        # remap saturated pixels to 255
        # use np.where and ufuncs to autovectorize
        # return ndarray of dtype uint8
        return np.where(x == -9999, 0,                                  # noqa: E126, E128
               np.where(x < 0, 0,                                       # noqa: E126, E128
               np.where(x > 10000, 255,                                 # noqa: E126, E128
                        np.floor_divide(x, 40)))).astype(np.uint8)      # noqa: E126, E128

    def get_metadata(self, bundle, field_name):
        if not self.xml_helper:
            relative_filename = '%s.xml' % (bundle.scene_entity_id,)
            absolute_filename = FileUtils.absolutize(bundle=bundle, filename=relative_filename)
            self.xml_helper = XmlHelper(absolute_filename)

        return self.xml_helper.retrieve(field_name)
