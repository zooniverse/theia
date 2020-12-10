from os import getenv, path, path
import csv

from ..abstract_operation import AbstractOperation
from panoptes_client import Panoptes, Project, Subject, SubjectSet
from theia.utils import PanoptesUtils

from PIL import Image

from datetime import datetime

class UploadSubject(AbstractOperation):
    def apply(self, filenames):
        if self.pipeline.multiple_subject_sets:
            scope = self.bundle
        else:
            scope = self.pipeline

        theia_authenticated_client = Panoptes(
            endpoint=PanoptesUtils.base_url(),
            client_id=PanoptesUtils.client_id(),
            client_secret=PanoptesUtils.client_secret()
        )

        with theia_authenticated_client:
            target_set = self._get_subject_set(scope, self.project.id, scope.name_subject_set())

            using_manifest = False
            metadata_dictionary = {}

            path_example = filenames[0]
            manifest_file_location = path.join((path.dirname(path_example) + "_interstitial_products"), "manifest.csv")
            if self.include_metadata and path.exists(manifest_file_location):
                using_manifest = True
                with open(manifest_file_location, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        metadata_dictionary[row['#filename']] = row

            for filename in filenames:
                img = Image.open(filename)
                img.save(filename, 'png')

                #This line might have to be done with os.path to translate across OSes
                name_only = filename.split("/")[len(filename.split("/")) - 1]

                metadata = {}
                if using_manifest:
                    metadata = metadata_dictionary[name_only]
                    print(metadata)

                new_subject = self._create_subject(self.project.id, filename, metadata=metadata)
                target_set.add(new_subject)


    def _get_subject_set(self, scope, project_id, set_name):
        subject_set = None
        if not scope.subject_set_id:
            subject_set = self._create_subject_set(project_id, set_name)
            scope.subject_set_id = subject_set.id
            scope.save()
        else:
            subject_set = SubjectSet.find(scope.subject_set_id)

        return subject_set

    def _create_subject(self, project_id, filename, metadata=None):
        subject = Subject()

        subject.links.project = Project.find(project_id)
        subject.add_location(filename)

        if metadata:
            subject.metadata.update(metadata)

        subject.save()

        return subject

    def _create_subject_set(self, project_id, subject_set_name):
        project = Project.find(project_id)

        subject_set = SubjectSet()
        subject_set.display_name = subject_set_name
        subject_set.links.project = project
        subject_set.save()

        return subject_set

    @property
    def include_metadata(self):
        if self.config['include_metadata']:
            return self.config['include_metadata']
        else:
            return False



