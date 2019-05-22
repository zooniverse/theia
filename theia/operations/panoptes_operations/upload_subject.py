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

        cls._connect()

        target_set = cls._get_subject_set(scope, project.id, scope.name_subject_set())
        new_subject = cls._create_subject(project.id, filename)
        target_set.add(new_subject)

    @classmethod
    def _connect(cls):
        Panoptes.connect(
            endpoint=PanoptesUtils.url(),
            client_id=PanoptesUtils.client_id(),
            client_secret=PanoptesUtils.client_secret()
        )


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
    def _create_subject(cls, project_id, filename, metadata=None):
        subject = Subject()

        subject.links.project = Project.find(project_id)
        subject.add_location(filename)

        if metadata:
            subject.metadata.update(metadata)

        subject.save()

        return subject

    @classmethod
    def _create_subject_set(cls, project_id, subject_set_name):
        project = Project.find(project_id)

        subject_set = SubjectSet()
        subject_set.display_name = subject_set_name
        subject_set.links.project = project
        subject_set.save()

        return subject_set
