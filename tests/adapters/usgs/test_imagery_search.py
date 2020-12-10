import pytest
from unittest import mock
from unittest.mock import patch, PropertyMock

import json
from theia.api.models import ImageryRequest
from theia.adapters.usgs import ImagerySearch


class TestImagerySearch:

    def test_adds_dataset_name(self):
        ir = ImageryRequest(wgs_row=1, wgs_path=2, dataset_name='ds9')
        search_obj = ImagerySearch.build_search(ir)
        assert search_obj['datasetName'] == 'ds9'

    def test_builds_value_filter(self):
        filter = ImagerySearch.value_filter('WRS Path', 5)
        assert filter == {'filterType': 'value', 'filterId': '5e83d0b81d20cee8', 'value': '5'}

    def test_builds_search_from_day_or_night(self):
        search = ImagerySearch.add_day_or_night({}, 'DAY')
        assert json.dumps(search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b83a03f8ee", "value": "DAY"}]}}}'

    def test_builds_search_from_row_and_path(self):
        search = ImagerySearch.add_wgs_row_and_path({}, 1, 10)
        assert json.dumps(search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'foo': 'bar'}, 1, 10)
        assert json.dumps(search) == '{"foo": "bar", "additionalCriteria": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'sceneFilter': {'metadataFilter': {}}}, 1, 10)
        assert json.dumps(search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'sceneFilter': {'metadataFilter': {'filterType': 'and', 'childFilters': []}}}, 1, 10)  # noqa: E501
        assert json.dumps(search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'sceneFilter': {'metadataFilter': {'filterType': 'and', 'childFilters': ['blah']}}}, 1, 10)  # noqa: E501
        assert json.dumps(search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": ["blah", {"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

    def test_builds_search_from_scene_cloud_cover(self):
        search = ImagerySearch.add_scene_cloud_cover({}, 20)
        assert json.dumps(search) == '{"sceneFilter": {"cloudCoverFilter": {"max": 20, "min": 0}}}'