"""Standard converters for PyFlowBase package
Console related functions"""  # pylint: disable=invalid-name

from typing import TYPE_CHECKING

# import the converter base from the PythonExporter package
from PyFlow.Packages.PythonExporter.Exporters.converter_base import (  # pylint: disable=import-error, no-name-in-module # type: ignore
    ConverterBase
)
if TYPE_CHECKING:
    from ..Exporters.converter_base import ConverterBase


class PyCnvConsoleFunctions(ConverterBase):
    """Standard converters for PyFlowBase package Console related functions"""

    @staticmethod
    def cliexit(exporter, node, inpnames: str, *args, **kwargs):  # pylint: disable=unused-argument
        """Convert the cliexit node type"""
        # import sys
        exporter.add_import("sys")
        # call
        exporter.add_call("sys.exit(0)")
        # flag that we are processed
        exporter.set_node_processed(node)
        # no yield
        if False:  # pylint: disable=using-constant-test
            yield

    @staticmethod
    def clearConsole(exporter, node, inpnames: str, *args, **kwargs):  # pylint: disable=unused-argument,invalid-name
        """Convert the clearConsole node type"""
        # export function definition
        if not exporter.is_node_function_processed(node):
            exporter.add_import("platform")
            exporter.add_import("os")
            exporter.add_sys_function("""def clearConsole():  # pylint: disable=invalid-name
    \"\"\"Clears the console screen in a platform independent way\"\"\"
    system = platform.system()
    if system != "":
        system = system.lower()
        if system in ("windows", "win32"):
            os.system("cls")
        if system in ("linux", "darwin", "linux2"):
            os.system("clear")
""")
            exporter.set_node_function_processed(node)
        # export call
        exporter.add_call("clearConsole()")
        exporter.set_node_processed(node)
        yield 'outExec'


    @staticmethod
    def consoleOutput(exporter, node, inpnames: str, *args, **kwargs):  # pylint: disable=unused-argument,invalid-name
        """Convert the consoleOutput node type"""
        exporter.add_call(f"print({', '.join(inpnames)})")
        exporter.set_node_processed(node)
        yield 'outExec'
