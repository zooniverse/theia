import json
from theia.api.models import ImageryRequest
from theia.adapters.usgs import ImagerySearch


class TestImagerySearch:
    def test_search_build_overview(self):
        imageryRequest = ImageryRequest(
            dataset_name='ds9',
            wgs_row=23,
            wgs_path=47,
            max_cloud_cover=65
        )
        search_obj = ImagerySearch.build_search(imageryRequest)
        print("SEARCH OBJ")
        print(search_obj)
        assert search_obj == {
            'datasetName': 'ds9',
            'sceneFilter': {
                'metadataFilter': {
                    'filterType': 'and',
                    'childFilters': [
                        {'filterType': 'value', 'filterId': '5e83d0b81d20cee8', 'value': '47'},
                        {'filterType': 'value', 'filterId': '5e83d0b849ed5ee7', 'value': '23'},
                        {'filterType': 'value', 'filterId': '5e83d0b83a03f8ee', 'value': 'DAY'}
                    ]
                },
                'cloudCoverFilter': {'max': 65, 'min': 0}
            }
        }

    def test_adds_dataset_name(self):
        imageryRequest = ImageryRequest(dataset_name='ds9')
        search_obj = ImagerySearch.build_search(imageryRequest)
        assert search_obj['datasetName'] == 'ds9'

    def test_builds_value_filter(self):
        filter = ImagerySearch.value_filter('WRS Path', 5)
        assert filter == {'filterType': 'value', 'filterId': '5e83d0b81d20cee8', 'value': '5'}

    def test_builds_search_from_day_or_night(self):
        search = ImagerySearch.add_day_or_night({}, 'DAY')
        assert json.dumps(
            search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b83a03f8ee", "value": "DAY"}]}}}'

    def test_builds_search_from_row_and_path(self):
        search = ImagerySearch.add_wgs_row_and_path({}, 1, 10)
        assert json.dumps(
            search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path({'sceneFilter': {'metadataFilter': {}}}, 1, 10)
        assert json.dumps(
            search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path(
            {'sceneFilter': {'metadataFilter': {'filterType': 'and', 'childFilters': []}}}, 1, 10)  # noqa: E501
        assert json.dumps(
            search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": [{"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

        search = ImagerySearch.add_wgs_row_and_path(
            {'sceneFilter': {'metadataFilter': {'filterType': 'and', 'childFilters': ['blah']}}}, 1, 10)  # noqa: E501
        assert json.dumps(
            search) == '{"sceneFilter": {"metadataFilter": {"filterType": "and", "childFilters": ["blah", {"filterType": "value", "filterId": "5e83d0b81d20cee8", "value": "10"}, {"filterType": "value", "filterId": "5e83d0b849ed5ee7", "value": "1"}]}}}'  # noqa: E501

    def test_builds_search_from_scene_cloud_cover(self):
        search = ImagerySearch.add_scene_cloud_cover({}, 20)
        assert json.dumps(search) == '{"sceneFilter": {"cloudCoverFilter": {"max": 20, "min": 0}}}'
