from django.test import TestCase
from theia.api.models import ImageryRequest, ImagerySearch

class TestImagerySearch(TestCase):
    def test_builds_search_from_row_and_path(self):
        imagery_request = ImageryRequest(
            dataset_name='LANDSAT_8_C1',
            project_id=123,
            wgs_row=28,
            wgs_path=46
        )

        # assert imagery_request.build_search() == '{ "datasetName": "LANDSAT_8_C1" , "additionalCriteria": { "filterType": "and", "childFilters": [{ "filterType": "value", "fieldId": 20514, "value": 28 }, { "filterType": "value", "fieldId": 20516, "value": 46 }]}}'