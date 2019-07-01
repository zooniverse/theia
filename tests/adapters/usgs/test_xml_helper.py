import pytest
from unittest import TestCase
from unittest.mock import patch, PropertyMock, call, ANY

from theia.adapters.usgs import XmlHelper


class TestXmlHelper(TestCase):
    @patch('theia.adapters.usgs.XmlHelper.get_tree')
    def test_resolve(self, mock_get_tree):
        mock_xpath = mock_get_tree.return_value.xpath
        helper = XmlHelper('foo.xml')
        helper.resolve('acquired_date')
        helper.resolve('some invalid field name')

        mock_xpath.assert_has_calls([
            call(XmlHelper.METADATA_PATHS['acquired_date'], namespaces=ANY),
            call(None, namespaces=ANY)
        ])
