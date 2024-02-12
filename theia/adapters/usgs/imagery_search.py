class ImagerySearch:
    additional_field_ids = {
        "WRS Path": "5e83d0b81d20cee8",
        "WRS Row": "5e83d0b849ed5ee7",
        "Day/Night Indicator": "5e83d0b83a03f8ee",
    }

    @classmethod
    def build_search(cls, imagery_request):
        search = {}
        search['datasetName'] = imagery_request.dataset_name
        if imagery_request.dataset_name is None:
            search['datasetName'] = 'LANDSAT_OT_C2_L2'

        if imagery_request.wgs_row and imagery_request.wgs_path:
            cls.add_wgs_row_and_path(search, row=imagery_request.wgs_row, path=imagery_request.wgs_path)

        cls.add_day_or_night(search)
        cls.add_scene_cloud_cover(search, imagery_request.max_cloud_cover or 100)

        return search

    @classmethod
    def add_day_or_night(cls, search, day_or_night='DAY'):
        filters = cls.get_filters(search)
        filters.append(cls.value_filter('Day/Night Indicator', day_or_night))
        return search

    @classmethod
    def add_scene_cloud_cover(cls, search, high):
        search.setdefault('sceneFilter', {})
        search["sceneFilter"]["cloudCoverFilter"] = {"max": high, "min": 0}
        return search

    @classmethod
    def add_wgs_row_and_path(cls, search, row, path):
        filters = cls.get_filters(search)
        filters.append(cls.value_filter('WRS Path', path))
        filters.append(cls.value_filter('WRS Row', row))
        return search

    @classmethod
    def get_filters(cls, search):
        search.setdefault('sceneFilter', {})
        search['sceneFilter'].setdefault('metadataFilter', {})
        search['sceneFilter']['metadataFilter'].setdefault('filterType', 'and')
        search['sceneFilter']['metadataFilter'].setdefault('childFilters', [])

        return search['sceneFilter']['metadataFilter']['childFilters']

    @classmethod
    def value_filter(cls, field_name, field_value):
        return {
            'filterType': 'value',
            'filterId': cls.additional_field_ids[field_name],
            'value': str(field_value)
        }
