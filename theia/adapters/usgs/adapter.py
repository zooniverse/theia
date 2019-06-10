from theia.api import models
from .imagery_search import ImagerySearch
from .eros_wrapper import ErosWrapper
from .espa_wrapper import EspaWrapper
from .tasks import wait_for_scene
from theia.utils import FileUtils

import os.path
import platform
import urllib.request


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
