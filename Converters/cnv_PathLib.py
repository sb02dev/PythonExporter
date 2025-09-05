"""Standard converters for PyFlowBase package
PathLib Function Library"""  # pylint: disable=invalid-name

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


class PyCnvPathLib(ConverterBase):
    """Standard converters for PyFlowBase package FlowControl nodes"""

    @staticmethod
    def func_join(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Join node"""
        exporter.add_import("os")
        return "return os.path.join(base, *paths)\n"
