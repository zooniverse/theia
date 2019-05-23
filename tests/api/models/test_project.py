
import pytest
from unittest.mock import patch

from django.test import TestCase
from theia.api.models import Project

class TestProject(TestCase):
    def test____str__(self):
        project = Project(name='foo')
        assert(project.__str__()=='foo')
