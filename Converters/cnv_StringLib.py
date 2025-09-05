"""Standard converters for PyFlowBase package
StringLib functions""" # pylint: disable=invalid-name

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


class PyCnvStringLib(ConverterBase):
    """Standard converters for PyFlowBase package StringLib functions"""

    @staticmethod
    def startsWith(exporter: PythonExporterImpl,
                    node: NodeBase,
                    inpnames: list[str],  # pylint: disable=unused-argument
                    *args, **kwargs):  # pylint: disable=unused-argument
        """Convert the startsWith node type"""
        # call
        exporter.add_call(
            f"{exporter.get_out_list(node, post=' = ')}" +
            f"{inpnames[0]}.startswith({inpnames[1]})")
        # flag that we are processed
        exporter.set_node_processed(node)
        # no yield
        if False:  # pylint: disable=using-constant-test
            yield

    @staticmethod
    def call_concat(exporter: PythonExporterImpl,
                    node: NodeBase,
                    inpnames: list[str],  # pylint: disable=unused-argument
                    *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Concat node"""
        return f"{exporter.get_out_list(node, post=' = ')}str({inpnames[0]}) + str({inpnames[1]})"
