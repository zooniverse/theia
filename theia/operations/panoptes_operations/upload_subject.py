from os import getenv, path, listdir
import csv

from ..abstract_operation import AbstractOperation
from panoptes_client import Panoptes, Project, Subject, SubjectSet
from theia.utils import PanoptesUtils

from PIL import Image

from datetime import datetime, timedelta

class UploadSubject(AbstractOperation):
    def apply(self, accepted_filenames):
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

            path_example = accepted_filenames[0]
            accepted_manifest_file_location = path.join((path.dirname(path_example) + "_interstitial_products"), "manifest.csv")
            
            if self.include_metadata and path.exists(accepted_manifest_file_location):
                using_manifest = True
                with open(accepted_manifest_file_location, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        metadata_dictionary[row['#filename']] = row

            for accepted_filename in accepted_filenames:
                img = Image.open(accepted_filename)
                img.save(accepted_filename, 'png')

                #This line might have to be done with os.path to translate across OSes
                name_only = accepted_filename.split("/")[len(accepted_filename.split("/")) - 1]

                metadata = {}
                if using_manifest:
                    metadata = metadata_dictionary[name_only]

                new_subject = self._create_subject(self.project.id, accepted_filename, metadata=metadata)
                target_set.add(new_subject)

            
            ##### TODO: DELETE THIS LATER. ONLY APPLICABLE FOR FLOATING FORESTS RESEARCH TEAM DEBUGING ##### 

            self.upload_rejected_tiles(path_example, scope)
            ## CREATING MASKS SUBJECT SET/ UPLOAD 

            #### TODO: END OF DELETE. DELETE ABOVE FROM LAST TODO #### 


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

    ## TODO: METHODS TO DELETE ONLY FOR FLOATING FORESTS DEBUG

    def upload_mask_tiles(self, path_example, scope):
        masked_tile_location =  path.dirname(path_example) + "_interstitial_products"

    def upload_rejected_tiles(self, path_example, scope):
        rejected_tile_location =  path.dirname(path_example) + "_interstitial_products/rejected"
    
        rejected_tiles = [rejected_file for rejected_file in listdir(rejected_tile_location) if (path.isfile(path.join(rejected_tile_location, rejected_file)) and rejected_file.endswith('.png'))]
        rejected_metadata_dict = {}

        rejected_tile_manifest_location = path.join(rejected_tile_location, "rejected.csv")

        if self.include_metadata and path.exists(rejected_tile_manifest_location):
            using_manifest = True
            with open(rejected_tile_manifest_location, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    rejected_metadata_dict[row['#filename']] = row

        rejected_subject_set = self._create_subject_set(self.project.id, scope.name_subject_set()+ ' rejected')

        for rejected_filename in rejected_tiles:
            try:
                rejected_file_path = path.join(rejected_tile_location, rejected_filename)
                # img = Image.open(rejected_file_path)
                # img.save(rejected_filename, 'png')

                name_only = rejected_filename.split("/")[len(rejected_filename.split("/")) - 1]

                metadata = {}
                if using_manifest:
                    metadata = rejected_metadata_dict[name_only]
                print('MDY114 REJECTED FILE NAME')

                # new_subject = self._create_subject(self.project.id, rejected_filename, metadata=metadata)
                new_subject = self._create_subject(self.project.id, rejected_file_path, metadata=metadata)
                rejected_subject_set.add(new_subject)
            except Exception as rejected_file_upload_err:
                print(rejected_file_upload_err)
                pass
    @property
    def include_metadata(self):
        if self.config['include_metadata']:
            return self.config['include_metadata']
        else:
            return False



