"""Standard converters for PyFlowBase package
General nodes"""  # pylint: disable=invalid-name

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


class PyCnvGeneral(ConverterBase):
    """Standard converters for PyFlowBase package General nodes"""

    @staticmethod
    def call_makeArray(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the MakeArray node"""
        linebeg = f"{exporter.get_out_list(node, post=' = ')}"
        linestart = ' '*len(linebeg)
        tolist_str = f"{(', \n'+linestart).join(inpnames[:-2])}], True\n"
        return linebeg+tolist_str
