from abc import ABC, abstractmethod

from theia.adapters import adapters
from theia.utils import FileUtils

class AbstractOperation(ABC):
    def __init__(self, bundle):
        self._bundle = bundle
        super().__init__()

    @property
    def bundle(self):
        return self._bundle

    @property
    def imagery_request(self):
        return self.bundle.imagery_request

    @property
    def pipeline_stage(self):
        return self.bundle.current_stage

    @property
    def output_extension(self):
        return self.pipeline_stage.output_format

    @property
    def pipeline(self):
        return self.imagery_request.pipeline

    @property
    def adapter(self):
        return adapters[self.imagery_request.adapter_name]

    @property
    def dataset_name(self):
        return self.imagery_request.dataset_name

    @property
    def select_images(self):
        return self.pipeline_stage.select_images

    @property
    def config(self):
        return self.pipeline_stage.config

    @property
    def sort_order(self):
        return self.pipeline_stage.sort_order

    @abstractmethod
    def apply(self, filenames):
        pass

    def get_new_version(self, filename):
        if not self.output_extension:
            return FileUtils.version_filename(filename, self.sort_order)
        else:
            # TODO: this should change the extension obviously
            return FileUtils.version_filename(filename, self.sort_order)

    def get_new_filename(self, filename):
        return self.get_new_version(
            FileUtils.absolutize(
                bundle=self.bundle,
                filename=self.adapter.construct_filename(self.bundle, filename)
            )
        )