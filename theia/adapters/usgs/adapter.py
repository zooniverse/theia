from theia.api import models
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
        for scene in scenes:
            result = EspaWrapper.order_all(scene, 'sr')
            for item in result:
                req = models.RequestedScene.objects.create(**{**item, **{'imagery_request': imagery_request}})
                wait_for_scene.delay(req.id)

    @classmethod
    def resolve_image(cls, scene_id, dataset_name, semantic_image_name):
        return '%s_sr_%s.tif' % (scene_id, semantic_image_name)

    @classmethod
    def acquire_image(cls, imagery_request):
        pass
