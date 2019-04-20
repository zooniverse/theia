from .imagery_request import ImageryRequest
import json

class ImagerySearch:
    additional_field_ids = {
        "WRS Path": 20514,
        "WRS Row": 20516
    }

    def __init__(imagery_request):
        return self

    def build_search(self):
        return ''

    @classmethod
    def add_wgs_row_and_path(cls, search, row, path):
        search.setdefault('additional_criteria', {})
        search['additional_criteria'].setdefault('filterType', 'and')
        search['additional_criteria'].setdefault('childFilters', [])

        filters = search['additional_criteria']['childFilters']
        filters.append(cls.value_filter('WRS Path', path))
        filters.append(cls.value_filter('WRS Row', row))
        return search

    @classmethod
    def value_filter(cls, field_name, field_value):
        return {
            'filterType': 'value',
            'fieldId': cls.additional_field_ids[field_name],
            'value': field_value
        }