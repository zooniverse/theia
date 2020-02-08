from os import getenv

from ..abstract_operation import AbstractOperation
from panoptes_client import Panoptes, Project, Subject, SubjectSet
from theia.utils import PanoptesUtils


class UploadSubject(AbstractOperation):
    def apply(self, filenames):
        if self.pipeline.multiple_subject_sets:
            scope = self.bundle
        else:
            scope = self.pipeline

        self.authenticated_panoptes = Panoptes(
             endpoint=PanoptesUtils.base_url(),
             client_id=PanoptesUtils.client_id(),
             client_secret=PanoptesUtils.client_secret()
        )

        self.authenticated_panoptes.bearer_token = self.imagery_request.bearer_token
        self.authenticated_panoptes.logged_in = True
        self.authenticated_panoptes.refresh_token = self.imagery_request.refresh_token
        bearer_expiry = datetime.strptime(self.imagery_request.bearer_expiry, "%Y-%m-%d %H:%M:%S.%f")
        self.authenticated_panoptes.bearer_expires = (bearer_expiry)

        with self.authenticated_panoptes:
            target_set = self._get_subject_set(scope, self.project.id, scope.name_subject_set())

            for filename in filenames:
                new_subject = self._create_subject(self.project.id, filename)
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
