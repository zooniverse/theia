class ImagerySearch:
    additional_field_ids = {
        "WRS Path": 20514,
        "WRS Row": 20516
    }

    def __init__(imagery_request):
        return self

    @classmethod
    def build_search(cls, imagery_request):
        return {}

    @classmethod
    def add_dataset_name(cls, search, name):
        search['datasetName'] = name
        return search

    @classmethod
    def add_wgs_row_and_path(cls, search, row, path):
        search.setdefault('additionalCriteria', {})
        search['additionalCriteria'].setdefault('filterType', 'and')
        search['additionalCriteria'].setdefault('childFilters', [])

        filters = search['additionalCriteria']['childFilters']
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