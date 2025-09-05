"""Standard converters for PyFlowBase package
BoolLib Function Library"""  # pylint: disable=invalid-name

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


class PyCnvBoolLib(ConverterBase):
    """Standard converters for PyFlowBase package BoolLib Function Library nodes"""

    @staticmethod
    def call_boolAnd(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Join node"""
        return f"{exporter.get_out_list(node, post=' = ')}({inpnames[0]} and {inpnames[1]})"

    @staticmethod
    def call_boolNot(exporter: PythonExporterImpl,
                     node: NodeBase,
                     inpnames: list[str],  # pylint: disable=unused-argument
                     *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Join node"""
        return f"{exporter.get_out_list(node, post=' = ')}(not {inpnames[0]})"
