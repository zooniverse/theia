from usgs import ErosWrapper


class TestErosWrapper:
    def test_connect(self):
        result = ErosWrapper.connect()
        assert not not result

    def test_access_level(self):
        result = ErosWrapper.access_level()
        assert result == 'user'
