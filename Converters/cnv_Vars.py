"""Standard converters for Variables handling"""  # pylint: disable=invalid-name

from typing import TYPE_CHECKING

from PyFlow.Core import NodeBase

# import the converter base from the PythonExporter package
from PyFlow.Packages.PythonExporter.Exporters.converter_base import (  # pylint: disable=import-error, no-name-in-module # type: ignore
    ConverterBase
)
from PyFlow.Packages.PythonExporter.Exporters.implementation import (  # pylint: disable=import-error, no-name-in-module # type: ignore
    PythonExporterImpl
)
if TYPE_CHECKING:
    from ..Exporters.converter_base import ConverterBase
    from ..Exporters.implementation import PythonExporterImpl


class PyCnvVariables(ConverterBase):
    """Standard converters for Variables handling"""

    @staticmethod
    def getVar(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Variable getter node"""
        # export the function definition
        if not exporter.is_node_function_processed(node):
            exporter.add_sys_function("def getVar(varname):\n    return VARS[varname]\n")
            exporter.set_node_function_processed(node)
        # export the call
        exporter.add_call(f"{exporter.get_out_list(node, post=' = ')}" +
                          f"getVar({repr(node.var.name)})") # type: ignore
        exporter.set_node_processed(node)
        # pure function
        if False:  # pylint: disable=using-constant-test
            yield


    @staticmethod
    def setVar(exporter: PythonExporterImpl,
               node: NodeBase,
               inpnames: list[str],  # pylint: disable=unused-argument
               *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Variable setter node"""
        # export the function definition
        if not exporter.is_node_function_processed(node):
            exporter.add_sys_function(
                "def setVar(varname, value):\n    VARS[varname] = value\n    return value\n")
            exporter.set_node_function_processed(node)
        # export the call
        exporter.add_call(f"{exporter.get_out_list(node, post=' = ')}" +
                          f"setVar({', '.join([repr(node.var.name)]+inpnames)})") # type: ignore
        exporter.set_node_processed(node)
        # pure function
        if False:  # pylint: disable=using-constant-test
            yield
