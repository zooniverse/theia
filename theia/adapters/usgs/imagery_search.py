class ImagerySearch:
    additional_field_ids = {
        "WRS Path": 20514,
        "Scene Cloud Cover": 20515,
        "WRS Row": 20516
    }

    @classmethod
    def build_search(cls, imagery_request):
        search = {}

        cls.add_dataset_name(search, imagery_request.dataset_name)

        if imagery_request.wgs_row and imagery_request.wgs_path:
            cls.add_wgs_row_and_path(search, imagery_request.wgs_row, imagery_request.wgs_path)

        return search

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
