import os, pytest
from lxml import etree
from unittest import TestCase
from unittest.mock import patch, PropertyMock, call, ANY

from theia.adapters.usgs import XmlHelper


class TestXmlHelper(TestCase):
    @classmethod
    def minimal_test_file(cls):
        return os.path.join(os.getcwd(), 'tests', 'adapters', 'usgs', 'minimal.xml')

    @classmethod
    def full_test_file(cls):
        return os.path.join(os.getcwd(), 'tests', 'adapters', 'usgs', 'full.xml')

    def test_resolve(self):
        'it resolves the name of a field to the path, with None if field name unknown'
        helper = XmlHelper('minimal.xml')
        assert(helper.resolve('acquired_date')=='espa:global_metadata/espa:acquisition_date/text()')
        assert(helper.resolve('some invalid name')==None)

    @patch('lxml.etree.parse', wraps=etree.parse)
    def test_get_tree(self, mock_parse):
        'it loads the xml tree and caches it for future reads'
        filename = TestXmlHelper.minimal_test_file()
        helper = XmlHelper(filename)
        tree = helper.get_tree()
        tree = helper.get_tree()

        mock_parse.assert_called_once()

    def test_get_tree2(self):
        'it gets a non-empty tree'
        filename = TestXmlHelper.minimal_test_file()
        helper = XmlHelper(filename)
        tree = helper.get_tree()
        assert(tree != None)

    def test_retrieve(self):
        'it retrieves text elements correctly from the xml file'
        filename = TestXmlHelper.minimal_test_file()
        helper = XmlHelper(filename)
        result = helper.retrieve('acquired_date')
        assert(result=='2013-06-08')

    def test_retrieve2(self):
        'it retrieves attributes correctly from the xml file'
        filename = TestXmlHelper.full_test_file()
        helper = XmlHelper(filename)
        result = helper.retrieve('scene_corner_UL_x')
        assert(result == '368100.000000')

    def test_retrieve3(self):
        'it retrieves numerical attributes correctly from the xml file'
        filename = TestXmlHelper.full_test_file()
        helper = XmlHelper(filename)
        result = helper.retrieve('utm_zone')
        assert(result == '15')
