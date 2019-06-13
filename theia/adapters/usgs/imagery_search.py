class ImagerySearch:
    additional_field_ids = {
        "WRS Path": 20514,
        "Scene Cloud Cover": 20515,
        "WRS Row": 20516,
        "Day/Night Indicator": 20513,
    }

    @classmethod
    def build_search(cls, imagery_request):
        search = {}

        cls.add_dataset_name(search, imagery_request.dataset_name)

        if imagery_request.wgs_row and imagery_request.wgs_path:
            cls.add_wgs_row_and_path(search, imagery_request.wgs_row, imagery_request.wgs_path)

        cls.add_day_or_night(search)
        cls.add_scene_cloud_cover(search, imagery_request.max_cloud_cover or 100)

        return search

    @classmethod
    def add_dataset_name(cls, search, name):
        search['datasetName'] = name
        return search

    @classmethod
    def add_day_or_night(cls, search, day_or_night='DAY'):
        filters = cls.get_additional_criteria(search)
        filters.append(cls.value_filter('Day/Night Indicator', day_or_night))
        return search

    @classmethod
    def add_scene_cloud_cover(cls, search, high):
        filters = cls.get_additional_criteria(search)
        filters.append(cls.range_filter('Scene Cloud Cover', '0', str(high)))
        return search

    @classmethod
    def add_wgs_row_and_path(cls, search, row, path):
        filters = cls.get_additional_criteria(search)
        filters.append(cls.value_filter('WRS Path', path))
        filters.append(cls.value_filter('WRS Row', row))
        return search

    @classmethod
    def get_additional_criteria(cls, search):
        search.setdefault('additionalCriteria', {})
        search['additionalCriteria'].setdefault('filterType', 'and')
        search['additionalCriteria'].setdefault('childFilters', [])

        return search['additionalCriteria']['childFilters']

    @classmethod
    def range_filter(cls, field_name, low, high):
        return {
            'filterType': 'between',
            'fieldId': cls.additional_field_ids[field_name],
            'firstValue': low,
            'secondValue': high
        }

    @classmethod
    def value_filter(cls, field_name, field_value):
        return {
            'filterType': 'value',
            'fieldId': cls.additional_field_ids[field_name],
            'value': field_value
        }
