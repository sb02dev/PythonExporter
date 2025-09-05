"""Runs tests on the test-graphs"""
import pytest
from tests import testhelper  # pylint: disable=import-error

@pytest.mark.parametrize("test_name", testhelper.get_test_names('flow'))
def test_flow(pycnv, testfolder, test_name):
    """Tests all graphs from the parameters"""
    testhelper.run_export_and_compare(pycnv, testfolder, "flow_"+test_name)


@pytest.mark.parametrize("test_name", testhelper.get_test_names('general'))
def test_general(pycnv, testfolder, test_name):
    """Tests all graphs from the parameters"""
    testhelper.run_export_and_compare(pycnv, testfolder, "general_"+test_name)


@pytest.mark.parametrize("test_name", testhelper.get_test_names('compound'))
def test_compound(pycnv, testfolder, test_name):
    """Tests all graphs from the parameters"""
    testhelper.run_export_and_compare(pycnv, testfolder, "compound_"+test_name)
