class Adapter:
    @classmethod
    def enum_datasets(cls):
        pass

    @classmethod
    def resolve_image(cls, scene_id, dataset_name, semantic_image_name):
        return '%s_sr_%s.tif' % (scene_id, semantic_image_name)

    @classmethod
    def acquire_image(cls, imagery_request):
        pass
