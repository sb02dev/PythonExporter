"""Standard converters for PyFlowBase package
FlowControl nodes"""  # pylint: disable=invalid-name

from typing import TYPE_CHECKING

from PyFlow.Core import NodeBase
from PyFlow.Core.PyCodeCompiler import Py3CodeCompiler

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


class PyCnvFlowControls(ConverterBase):
    """Standard converters for PyFlowBase package FlowControl nodes"""

    @staticmethod
    def compound(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Compound node"""
        # export function definition
        if not exporter.is_node_function_processed(node):
            # run in subexporter
            subexporter = PythonExporterImpl(
                node.rawGraph, # type: ignore
                exporter.converter_classes,
                1,
                exporter.exported_node_functions
            )
            execinpins = [pin for pin in node.orderedInputs.values() if pin.isExec()]
            if len(execinpins)>0:
                # TODO: why the first pin? actually this is the only place where input
                # exec pins can lead to different outcomes: on normal nodes it just
                # executes the node's compute, but here different paths can be connected
                # to different exec pins. so we need an argument which tells which exec
                # pin should be executed. that could be passed conditionally as a kwarg.
                # how does this work in the main execution engine?
                firstexecpin = list(execinpins[0].affects)[0]
                subexporter.export_from_pin(firstexecpin)
            else:
                # TODO: here again the first graphOutput is processed. but from the input pin
                # we could actually follow to the real graphOutput needed
                # TODO: process_node could yield back from graphOutput nodes when they are
                # reached with exec and then we can yield it further through our exec pins.
                # or just give a callback to process_node which will call exporter.call_named_pin.
                # TODO: consider a "parent exporter" concept and make this handled in the exporter?
                subexporter.process_node(
                    node.rawGraph.getNodesList( # type: ignore
                        classNameFilters=["graphOutputs"]
                    )[0]
                )
            # collect the results
            exporter.collect_subexporter_results(subexporter, node)
            # don't flag the type as exported: because each compound node has to be exported
            # separately (inner graph is different)
        # export call
        exporter.add_call(f"{exporter.get_out_list(node, post=' = ')}" +
                          f"{node.name}({', '.join(inpnames)})")
        exporter.set_node_processed(node)
        # call first connected execute pin
        connexecoutpins = [pin
                           for pin in node.orderedOutputs.values()
                           if pin.isExec() and pin.hasConnections()]
        if len(connexecoutpins)>0:
            yield connexecoutpins[0].getName()
                # TODO: this calls the first connected pin, however there
                # could be multiple, which should be called from inside the
                # node


    @staticmethod
    def call_graphOutputs(exporter: PythonExporterImpl,  # pylint: disable=unused-argument
                          node: NodeBase,  # pylint: disable=unused-argument
                          inpnames: list[str],  # pylint: disable=unused-argument
                          *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the GraphOutputs node"""
        if len(inpnames)==0:
            return ''
        return f"return {', '.join(inpnames)}"


    @staticmethod
    def sequence(exporter: PythonExporterImpl,
                 node: NodeBase,
                 inpnames: list[str],  # pylint: disable=unused-argument
                 *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Sequence node"""
        # flag that this is processed
        exporter.set_node_processed(node)
        # call execute pins
        outs = sorted(list(node.outputs.values()), key=lambda pin: int(pin.name))
        for pin in outs:
            if pin.isExec():
                yield pin.name # TODO: consider: `exporter.call_named_pin(pin)`


    @staticmethod
    def branch(exporter: PythonExporterImpl,
               node: NodeBase,
               inpnames: list[str],  # pylint: disable=unused-argument
               *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the Branch node"""
        hasTrue = node.getPinByName('True').hasConnections()  # type: ignore
        hasFalse = node.getPinByName('False').hasConnections()  # type: ignore
        if not hasTrue and not hasFalse:
            return
        # flag that we are processed
        exporter.set_node_processed(node)
        # convert the true branch
        exporter.add_call(f"if {inpnames[0]}:\n")
        if hasTrue:
            exporter.increase_indent()
            yield 'True'
            exporter.decrease_indent()
        else:
            exporter.add_call("  pass")
        # convert the false branch
        if hasFalse:
            exporter.add_call("else:\n")
            exporter.increase_indent()
            yield 'False'
            exporter.decrease_indent()
        # call 'After' pin
        yield 'After'


    @staticmethod
    def pythonNode(exporter: PythonExporterImpl,
               node: NodeBase,
               inpnames: list[str],  # pylint: disable=unused-argument
               *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the PythonNode node"""
        # export function definition
        mem = Py3CodeCompiler().compile(node.nodeData, node.getName(), {})  # type: ignore
        inputs = ', '.join([pin.name
                            for pin in node.orderedInputs.values()
                            if not pin.isExec()])
        exporter.add_function(f"def {node.name}({inputs}):\n{
            mem['func_python'](exporter,
                               node, *args, **kwargs)}\n")
        # export call
        exporter.add_call(f"{exporter.get_out_list(node, post=' = ')}{node.name}({
            ', '.join(inpnames)})\n")
        exporter.set_node_processed(node)
        # call execute pins
        execoutpins = [pin
                       for pin in node.orderedOutputs.values()
                       if pin.isExec()]
        if len(execoutpins)>0:
            yield execoutpins[0].name
        # TODO: consider: these execpins should be called from `mem['func_python']`


    @staticmethod
    def rerouteExecs(exporter: PythonExporterImpl,
                     node: NodeBase,
                     inpnames: list[str],  # pylint: disable=unused-argument
                     *args, **kwargs):  # pylint: disable=unused-argument
        """Converts the reroute exec nodes"""
        exporter.set_node_processed(node)
        yield 'out'
