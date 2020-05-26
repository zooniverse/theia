from abc import ABC, abstractmethod
from os.path import splitext
import os

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
    def pipeline(self):
        return self.bundle.pipeline

    @property
    def project(self):
        return self.pipeline.project

    @property
    def adapter(self):
        return adapters[self.imagery_request.adapter_name]()

    @property
    def adapter_name(self):
        return self.imagery_request.adapter_name

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

    @property
    def output_directory(self):
        output_directory_name = self.pipeline_stage.output_filename
        return FileUtils.absolutize(bundle=self.bundle, filename=output_directory_name)

    @property
    def manifest_directory(self):
        manifest_directory_name = self.pipeline_stage.interstitial_product_location
        return FileUtils.absolutize(bundle=self.bundle, filename=manifest_directory_name)


    @property
    def output_extension(self):
        if self.pipeline_stage.output_format:
            return self.pipeline_stage.output_format
        else:
            return "tif" #We default to tif because that is the format of the incoming ESPA data

    @abstractmethod
    def apply(self, filenames):
        pass  # pragma: nocover

    def establish_output_directory(self):
        if not os.path.isdir(self.output_directory):
            os.mkdir(self.output_directory)

    def get_new_version(self, file_title):
        file_title = FileUtils.version_filename(file_title, self.sort_order)
        filename = splitext(file_title)[0] + '.' + self.output_extension

        return filename

    def get_new_filename(self, filename):
        return self.get_new_version(
            FileUtils.absolutize(
                bundle=self.bundle,
                filename=self.adapter.construct_filename(self.bundle, filename)
            )
        )
