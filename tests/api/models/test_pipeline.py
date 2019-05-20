
import pytest
from unittest.mock import patch

from django.test import TestCase
from theia.api.models import Pipeline, Project

class TestPipeline(TestCase):
    def test_name_subject_set(self):
        pipeline = Pipeline(name='my pipeline')
        assert(pipeline.name_subject_set()=='my pipeline Pipeline')

    @pytest.mark.focus
    def test___str__(self):
        project = Project(name='proj')
        pipeline = Pipeline(name='pipe', project=project)
        assert(pipeline.__str__()=='proj | pipe')
