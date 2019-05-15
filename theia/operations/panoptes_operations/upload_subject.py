from os import getenv
from panoptes_client import Panoptes, Project, Subject, SubjectSet
from .utils import PanoptesUtils


class UploadSubject:
    @classmethod
    def apply(cls, filename, bundle):
        pipeline = bundle.pipeline
        project = pipeline.project

        target_set_id = None

        if pipeline.multiple_subject_sets:
            scope = bundle
        else:
            scope = pipeline

        Panoptes.connect(
            endpoint=getenv('PANOPTES_URL', 'https://panoptes.zooniverse.org/'),
            client_id=getenv('PANOPTES_CLIENT_ID'),
            client_secret=getenv('PANOPTES_CLIENT_SECRET')
        )

        target_set = cls._get_subject_set(scope, project.id, bundle.scene_entity_id)
        new_subject = cls._create_subject(project, filename)
        target_set.add(new_subject)

    @classmethod
    def _get_subject_set(cls, scope, project_id, set_name):
        subject_set = None
        if not scope.subject_set_id:
            subject_set = cls._create_subject_set(project_id, set_name)
            scope.subject_set_id = subject_set.id
            scope.save()
        else:
            subject_set = SubjectSet.find(scope.subject_set_id)

        return subject_set

    @classmethod
    def _create_subject(cls, project, filename, metadata=None):
        subject = Subject()

        subject.links.project = project
        subject.add_location(filename)

        if metadata:
            subject.metadata.update(metadata)

        subject.save()

        return subject

    @classmethod
    def _create_subject_set(cls, project_id, subject_set_name):
        project = Project.find(project_id)

        subject_set = SubjectSet()
        subject_set.links.project = project
        subject_set.display_name = subject_set_name
        subject_set.save()

        return subject_set
