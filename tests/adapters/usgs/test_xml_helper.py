import os, pytest
from lxml import etree
from unittest import TestCase
from unittest.mock import patch, PropertyMock, call, ANY

from theia.adapters.usgs import XmlHelper


class TestXmlHelper(TestCase):
    def test_resolve(self):
        'it resolves the name of a field to the path, with None if field name unknown'
        helper = XmlHelper('minimal.xml')
        assert(helper.resolve('acquired_date')=='espa:global_metadata/espa:acquisition_date/text()')
        assert(helper.resolve('some invalid name')==None)

    @patch('theia.adapters.usgs.XmlHelper.get_tree')
    def test_retrieve(self, mock_get_tree):
        'it tries to retrieve the correct path from the xml tree'
        mock_xpath = mock_get_tree.return_value.xpath
        helper = XmlHelper('foo.xml')
        helper.retrieve('acquired_date')
        helper.retrieve('some invalid field name')

        mock_xpath.assert_has_calls([
            call(XmlHelper.METADATA_PATHS['acquired_date'], namespaces=ANY),
            call(None, namespaces=ANY)
        ])

    @pytest.mark.focus
    @patch('lxml.etree.parse', wraps=etree.parse)
    def test_get_tree(self, mock_parse):
        'it loads the xml tree and caches it for future reads'
        filename = os.path.join(os.getcwd(), 'tests', 'adapters', 'usgs', 'minimal.xml')
        helper = XmlHelper(filename)
        tree = helper.get_tree()
        tree = helper.get_tree()

        mock_parse.assert_called_once()
