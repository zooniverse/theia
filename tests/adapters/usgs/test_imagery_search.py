import pytest
from unittest import mock
from unittest.mock import patch, PropertyMock

import json
from theia.api.models import ImageryRequest
from theia.adapters.usgs import ImagerySearch


class TestImagerySearch:
    @patch('theia.adapters.usgs.ImagerySearch.add_day_or_night')
    @patch('theia.adapters.usgs.ImagerySearch.add_scene_cloud_cover')
    @patch('theia.adapters.usgs.ImagerySearch.add_dataset_name')
    @patch('theia.adapters.usgs.ImagerySearch.add_wgs_row_and_path')
    def test_builds_path_row_search(self, mockAddPath, mockAddName, *args):
        ir = ImageryRequest(wgs_row=1, wgs_path=2, dataset_name='ds9')
        search_obj = ImagerySearch.build_search(ir)
        mockAddName.assert_called_once_with({}, 'ds9')
        mockAddPath.assert_called_once_with({}, 1, 2)
        assert search_obj == {}

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

    def test_builds_search_from_day_or_night(self):
        search = ImagerySearch.add_day_or_night({}, 'DAY')
        assert json.dumps(search) == '{"additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "value", "fieldId": 20513, "value": "DAY"}]}}'

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

    def test_builds_search_from_scene_cloud_cover(self):
        search = ImagerySearch.add_scene_cloud_cover({}, 20)
        assert json.dumps(search) == '{"additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "between", "fieldId": 20515, "firstValue": "0", "secondValue": "20"}]}}'