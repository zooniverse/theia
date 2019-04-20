import json
from django.test import TestCase
from theia.api.models import ImageryRequest, ImagerySearch

class TestImagerySearch(TestCase):
    def test_builds_value_filter(self):
        filter = ImagerySearch.value_filter('WRS Path', 5)
        assert filter == { 'filterType': 'value', 'fieldId': 20514, 'value': 5 }

    def test_builds_search_from_row_and_path(self):
        search = ImagerySearch.add_wgs_row_and_path({}, 1, 10)
        assert json.dumps(search) == '{"additional_criteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'

        search = ImagerySearch.add_wgs_row_and_path({'foo':'bar'}, 1, 10)
        assert json.dumps(search) == '{"foo": "bar", "additional_criteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'

        search = ImagerySearch.add_wgs_row_and_path({'additional_criteria': {}}, 1, 10)
        assert json.dumps(search) == '{"additional_criteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'

        search = ImagerySearch.add_wgs_row_and_path({'additional_criteria': {'filterType': 'and', 'childFilters': []}}, 1, 10)
        assert json.dumps(search) == '{"additional_criteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'

        search = ImagerySearch.add_wgs_row_and_path({'additional_criteria': {'filterType': 'and', 'childFilters': ['blah']}}, 1, 10)
        assert json.dumps(search) == '{"additional_criteria": {"filterType": "and", "childFilters": ["blah", {"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'