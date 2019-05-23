import pytest
from unittest.mock import patch

from theia.utils import FileUtils

class TestFileUtils:
    def test__version(self):
        assert(FileUtils._version('foo.bar', 7)=='foo_stage_07.bar')

    def test__unversion(self):
        assert(FileUtils._unversion('foo.bar')=='foo.bar')
        assert(FileUtils._unversion('foo_stage_03.bar')=='foo.bar')

    @patch('theia.utils.FileUtils._version', return_value='reversioned')
    @patch('theia.utils.FileUtils._unversion', return_value='unversioned')
    def test_version_filename(self, mockUn, mockRe):
        assert(FileUtils.version_filename('foo_stage_8.bar', 2)=='reversioned')
        mockUn.assert_called_once_with('foo_stage_8.bar')
        mockRe.assert_called_once_with('unversioned', 2)

    def test_locate_latest_version(self):
        assert(FileUtils.locate_latest_version('foo.bar', 3)=='foo.bar')

        with patch('os.path.isfile') as mockIsFile:
            mockIsFile.side_effect = [False, True]
            assert(FileUtils.locate_latest_version('foo.bar', 3)=='foo_stage_01.bar')
