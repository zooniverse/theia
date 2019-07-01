class Adapter:
    def enum_datasets(self):
        pass  # pragma: nocover

    def process_request(self, imagery_request):
        pass  # pragma: nocover

    def resolve_relative_image(self, bundle, semantic_image_name):
        pass  # pragma: nocover

    def retrieve(self, job_bundle):
        pass  # pragma: nocover

    def acquire_image(self, imagery_request):
        pass  # pragma: nocover

    def remap_pixel(self, pixel_value):
        pass  # pragma: nocover

    def construct_filename(self, bundle, suffix):
        pass  # pragma: nocover

    def get_metadata(self, bundle, field_name):
        pass  # pragma: nocover
