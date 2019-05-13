import json
from django.test import TestCase
from theia.api.models import ImageryRequest
from theia.adapters.usgs.imagery_search import ImagerySearch


class TestImagerySearch(TestCase):
    def test_builds_entire_search(self):
        # TODO: write this test
        ir = ImageryRequest()  # noqa

    def test_builds_value_filter(self):
        filter = ImagerySearch.value_filter('WRS Path', 5)
        assert filter == {'filterType': 'value', 'fieldId': 20514, 'value': 5}

    def test_builds_search_from_dataset_name(self):
        search = ImagerySearch.add_dataset_name({}, "L8")
        assert json.dumps(search) == '{"datasetName": "L8"}'

        search = ImagerySearch.add_dataset_name({'datasetName': 'L7'}, "L8")
        assert json.dumps(search) == '{"datasetName": "L8"}'

        search = ImagerySearch.add_dataset_name({'foo': 'bar'}, "L8")
        assert json.dumps(search) == '{"foo": "bar", "datasetName": "L8"}'

    def test_builds_search_from_row_and_path(self):
        search = ImagerySearch.add_wgs_row_and_path({}, 1, 10)
        assert json.dumps(search) == '{"additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'foo': 'bar'}, 1, 10)
        assert json.dumps(search) == '{"foo": "bar", "additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'additionalCriteria': {}}, 1, 10)
        assert json.dumps(search) == '{"additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'additionalCriteria': {'filterType': 'and', 'childFilters': []}}, 1, 10)  # noqa: E501
        assert json.dumps(search) == '{"additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'additionalCriteria': {'filterType': 'and', 'childFilters': ['blah']}}, 1, 10)  # noqa: E501
        assert json.dumps(search) == '{"additionalCriteria": {"filterType": "and", "childFilters": ["blah", {"filterType": "value", "fieldId": 20514, "value": 10}, {"filterType": "value", "fieldId": 20516, "value": 1}]}}'  # noqa: E501
