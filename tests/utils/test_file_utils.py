import pytest
from unittest.mock import patch
import tarfile

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
        mockUn.assert_called_once_with('foo_stage_8.bar', new_extension=None)
        mockRe.assert_called_once_with('unversioned', 2)

    @patch('glob.glob', side_effect=[[], [], [], []])
    def test_locate_latest_version_new(self, *args):
        assert(FileUtils.locate_latest_version('foo.bar', 3)=='foo.bar')

    @patch('glob.glob', side_effect=[[], ['foo_stage_01.bar']])
    @patch('os.path.isfile', return_value=True)
    def test_locate_latest_version_exists(self, *args):
        assert(FileUtils.locate_latest_version('foo.bar', 3)=='foo_stage_01.bar')

    @patch('os.path.isdir', return_value=False)
    @patch('os.mkdir')
    def test_untar(self, mockMkDir, mockIsDir):
        with patch.object(tarfile, 'open', autospec=True) as mockOpen:
            FileUtils.untar('some/zip/path', 'some/dir/path')
            mockOpen.assert_called_once_with('some/zip/path', 'r')
            mockIsDir.assert_called_once_with('some/dir/path')
            mockMkDir.assert_called_once_with('some/dir/path')
            mockOpen.return_value.__enter__.return_value.extractall.assert_called_once_with('some/dir/path')
