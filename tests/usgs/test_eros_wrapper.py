from usgs import ErosWrapper


class TestErosWrapper:
    def test_connect(self):
        result = ErosWrapper.connect()
        assert not not result

    def test_access_level(self):
        result = ErosWrapper.access_level()
        assert result == 'user'

    def test_parse_result_set(self):
        result = ErosWrapper.parse_result_set([])
        assert result == []

        result = ErosWrapper.parse_result_set(
            [{'displayId': 'aaaa', 'foo': 'bar'}]
        )
        assert result == ['aaaa']

        result = ErosWrapper.parse_result_set(
            [
                {'displayId': 'a', 'foo': 'bar'},
                {'displayId': 'b', 'foo': 'bar'},
            ]
        )
        assert result == ['a', 'b']