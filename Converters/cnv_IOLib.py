"""Standard converters for PyFlowBase package
IOLib Function Library"""  # pylint: disable=invalid-name

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


class PyCnvIOLib(ConverterBase):
    """Standard converters for PyFlowBase package IOLib Function Library nodes"""

    @staticmethod
    def readAllText(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the ReadAllText node"""
        # export function definition
        if not exporter.is_node_function_processed(node):
            exporter.add_sys_function("""def readAllText(file, encoding):
    with open(file, encoding=encoding) as f:
        try:
            return '\\n'.join(f.readlines()), None
        except Exception as e:
            return None, e.message
""")
            exporter.set_node_function_processed(node)
        # export call
        exporter.add_call(f"{exporter.get_out_list(node, post=' = ')}" + \
                          f"readAllText({', '.join(inpnames)})\n")
        exporter.set_node_processed(node)
        # call execute pin
        exporter.call_named_pin(node, 'outExec')
