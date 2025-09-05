"""Test configuration for PyFlow PythonExporter Package"""
import os
import json
from typing import Callable, NamedTuple
import pytest

from PyFlow import INITIALIZE, GET_PACKAGES
from PyFlow.Core.GraphManager import GraphManagerSingleton
from PyFlow.App import PyFlow as PyFlowApp


@pytest.fixture
def testfolder():
    """Gets the folder where the tests live"""
    return os.path.abspath(os.path.dirname(__file__))


MockPyFlowApp = NamedTuple('MockPyFlowApp', [
    ('graphManager', GraphManagerSingleton)
])

@pytest.fixture
def pyflowapp(testfolder):  # pylint: disable=redefined-outer-name
    """Initialize pyflow with ourselves as an additional module
    WARNING: if there is another package in the folder structure
    we cannot prevent it being loaded
    """
    pkgpath = os.path.abspath(os.path.join(testfolder, "../../../../.."))
    INITIALIZE([pkgpath])
    gman = GraphManagerSingleton()
    app = MockPyFlowApp(graphManager=gman)
    return app


PyCnvTest = NamedTuple('PyCnvTest', [
    ('app', MockPyFlowApp),
    ('graphLoader', Callable[[str], None]),
    ('exporter', Callable[[PyFlowApp, str], None])
])

@pytest.fixture
def pycnv(pyflowapp):  # pylint: disable=redefined-outer-name
    """A fixture getting the PyFlow references neccessary for the tests"""
    pkgs = GET_PACKAGES()
    pkg = pkgs["PythonExporter"]
    exporter_class = pkg.GetExporters()['PythonExporter']

    def graphLoader(gman: GraphManagerSingleton) -> Callable[[str], None]:  # type: ignore # pylint: disable=invalid-name
        def loader(fname: str):
            with open(fname, "r", encoding='utf8') as f:
                data = json.load(f)
            gman.get().deserialize(data)
            gman.get().selectGraphByName(data["activeGraph"])
        return loader

    return PyCnvTest(
        app = pyflowapp,
        graphLoader=graphLoader(pyflowapp.graphManager),
        exporter = exporter_class.doExport
    )
