"""Standard converters for PyFlowBase package
MathAbstractLib Function Library"""  # pylint: disable=invalid-name

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


class PyCnvMathAbstractLib(ConverterBase):
    """Standard converters for PyFlowBase package MathAbstractLib Function Library nodes"""

    @staticmethod
    def call_notEqual(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the NotEqual node"""
        return f"{exporter.get_out_list(node, post=' = ')}({inpnames[0]} != {inpnames[1]})"

    @staticmethod
    def call_multiply(exporter: PythonExporterImpl,
                      node: NodeBase,
                      inpnames: list[str],  # pylint: disable=unused-argument
                      *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Multiply node"""
        return f"{exporter.get_out_list(node, post=' = ')}({inpnames[0]} * {inpnames[1]})"


    @staticmethod
    def call_add(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Add node"""
        return f"{exporter.get_out_list(node, post=' = ')}({inpnames[0]} + {inpnames[1]})"


    @staticmethod
    def call_power(exporter: PythonExporterImpl,
                   node: NodeBase,
                   inpnames: list[str],  # pylint: disable=unused-argument
                   *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the NotEqual node"""
        exporter.add_import('math')
        return f"{exporter.get_out_list(node, post=' = ')}math.pow({inpnames[0]}, {inpnames[1]}), True"
