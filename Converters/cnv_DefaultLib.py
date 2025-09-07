"""Standard converters for PyFlowBase package
DefaultLib Function Library"""  # pylint: disable=invalid-name

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


class PyCnvDefaultLib(ConverterBase):
    """Standard converters for PyFlowBase package DefaultLib Function Library nodes"""

    @staticmethod
    def call_makeString(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Join node"""
        return f"{exporter.get_out_list(node, post=' = ')}{', '.join(inpnames)}"

    @staticmethod
    def call_select(exporter: PythonExporterImpl,
                        node: NodeBase,
                        inpnames: list[str],  # pylint: disable=unused-argument
                        *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Select node"""
        return f"{exporter.get_out_list(node, post=' = ')}" \
               f"{inpnames[0]} if {inpnames[2]} else {inpnames[1]}, {inpnames[2]}\n"

    @staticmethod
    def call_makeInt(exporter: PythonExporterImpl,
                     node: NodeBase,
                     inpnames: list[str],  # pylint: disable=unused-argument
                     *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the makeInt node"""
        return f"{exporter.get_out_list(node, post=' = ')}{', '.join(inpnames)}"


    @staticmethod
    def call_makeDictElement(exporter: PythonExporterImpl,
                             node: NodeBase,
                             inpnames: list[str],  # pylint: disable=unused-argument
                             *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the makeDictElement node"""
        return f"{exporter.get_out_list(node, post=' = ')}({', '.join(inpnames)})"


    @staticmethod
    def makeDict(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the makeDict node"""
        firstline = f"{exporter.get_out_list(node, post=' = ')}dict(["
        exporter.add_call(firstline +
                          f"{(',\n'+' '*len(firstline)).join(inpnames[1:])}]), True")


    @staticmethod
    def call_makeFloat(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the makeFloat node"""
        return f"{exporter.get_out_list(node, post=' = ')}{', '.join(inpnames)}"
