"""A node using a referenced compound as a function"""  # pylint: disable=invalid-name

from typing import TYPE_CHECKING, Optional, cast
import uuid

from PyFlow.Core.Common import clearSignal, PinSelectionGroup
from PyFlow.Core import NodeBase, PinBase, GraphBase
from PyFlow.Core.Common import PinOptions
from PyFlow.Packages.PyFlowBase.Nodes import FLOW_CONTROL_COLOR
from blinker import Signal

if TYPE_CHECKING:
    from ..Exporters.implementation import PythonExporterImpl
    from PyFlow.Packages.PyFlowBase.Nodes.compound import compound



class Function(NodeBase):
    """A node using a referenced compound as a function"""

    def __init__(self, name, uid=None):
        super().__init__(name, uid)

        self.bCacheEnabled = False
        self.pinExposed = Signal(object)  # type: ignore
        self.__inputsMap = {}
        self.__outputsMap = {}

        self.p_func_name = cast(PinBase, self.createInputPin(
            pinName='function',
            dataType='StringPin',
        ))
        self.p_func_name.setInputWidgetVariant('CompoundNamesWidget')
        self.p_func_name.dataBeenSet.connect(self.function_updated)

        self.headerColor = FLOW_CONTROL_COLOR


    def postCreate(self, jsonTemplate: Optional[dict] = None):
        super().postCreate(jsonTemplate)
        # recreate dynamically created pins
        if jsonTemplate is not None:
            inputs_map = self.namePinInputsMap
            for inp_json in jsonTemplate['inputs']:
                if inp_json['name'] not in inputs_map:
                    pin = cast(PinBase, self.createInputPin(inp_json['name'], inp_json['dataType']))
                    pin.deserialize(inp_json)
                else:
                    pin = inputs_map[inp_json['name']]
                pin.uid = uuid.UUID(inp_json['uuid'])

            outputs_map = self.namePinOutputsMap
            for out_json in jsonTemplate['outputs']:
                if out_json['name'] not in outputs_map:
                    pin = cast(PinBase, self.createOutputPin(
                        out_json['name'],
                        out_json['dataType']
                    ))
                    pin.deserialize(out_json)
                else:
                    pin = outputs_map[out_json['name']]
                pin.uid = uuid.UUID(out_json['uuid'])

        self.bCallable = self.isCallable()


    @staticmethod
    def category():  # type: ignore
        return 'FlowControl'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():  # type: ignore
        return 'Call a function'
    

    def function_updated(self, data):
        """Event fired when the function reference is changed"""
        self.sync_pins()

    def sync_pins(self):
        """Synchronize the pins of this node to those of the referenced function"""
        try:
            func_paths = self.getData('function').split('.')
            compound = self.get_function_compound(
                self.graph().graphManager.findRootGraph(),  # type: ignore # pylint: disable=not-callable
                func_paths)
        except Exception:
            return

        if compound is None:
            return

        # collect compound pins and create them, also remove old pins
        node_input_pins = self.namePinInputsMap
        for node_input_pin_name, node_input_pin in node_input_pins.items():
            if node_input_pin_name != 'function':
                if node_input_pin is self.__inputsMap:
                    node_input_pin.kill()
                clearSignal(node_input_pin.killed)
                self.__inputsMap.pop(node_input_pin)

        graph_input_pins = {}
        for out_pin in compound.orderedInputs.values():
            graph_input_pins[out_pin.name] = out_pin
            # create companion pin if needed
            self.on_graph_input_pin_created(out_pin)

        node_output_pins = self.namePinOutputsMap
        for node_output_pin_name, node_output_pin in node_output_pins.items():
            if node_output_pin in self.__outputsMap:
                node_output_pin.kill()
                clearSignal(node_output_pin.killed)
                self.__outputsMap.pop(node_output_pin)

        graph_output_pins = {}
        for in_pin in compound.orderedOutputs.values():
            graph_output_pins[in_pin.name] = in_pin
            # create companion pin if needed
            self.on_graph_output_pin_created(in_pin)


    def on_graph_input_pin_created(self, out_pin: PinBase):
        """Reaction when pin added to graphInputs node
        
        :param out_pin: output pin on graphInputs node
        :type out_pin: :class:`~OyFkiw.Core.PinBase.PinBase"""
        # add companion pin for graphInputs node's output pin
        subgraph_input_pin = cast(PinBase, self.createInputPin(
            out_pin.name,
            out_pin.__class__.__name__,
            out_pin.defaultValue(),
            out_pin.call,
            out_pin.structureType,
            out_pin.constraint,
            out_pin.structConstraint,
            group=cast(NodeBase, out_pin.owningNode()).name
        ))
        if subgraph_input_pin.isAny():
            subgraph_input_pin.supportedDataTypes = out_pin.supportedDataTypes
            subgraph_input_pin.enableOptions(
                PinOptions.AllowAny | PinOptions.DictElementSupported
            )
        self.__inputsMap[subgraph_input_pin] = out_pin
        self.pinExposed.send(subgraph_input_pin)


    def on_graph_output_pin_created(self, in_pin: PinBase):
        """Reaction when pin added to graphOutputs node
        
        :param out_pin: output pin on graphOutputs node
        :type out_pin: :class:`~OyFkiw.Core.PinBase.PinBase"""
        # add companion pin for graphOutputs node's input pin
        subgraph_output_pin = cast(PinBase, self.createOutputPin(
            in_pin.name,
            in_pin.__class__.__name__,
            in_pin.defaultValue(),
            in_pin.structureType,
            in_pin.constraint,
            in_pin.structConstraint,
            group=cast(NodeBase, in_pin.owningNode()).name
        ))
        if subgraph_output_pin.isAny():
            subgraph_output_pin.supportedDataTypes = in_pin.supportedDataTypes
            subgraph_output_pin.enableOptions(
                PinOptions.AllowAny | PinOptions.DictElementSupported
            )
        self.__outputsMap[subgraph_output_pin] = in_pin
        self.pinExposed.send(subgraph_output_pin)


    def get_function_compound(self, graph: GraphBase, paths: list[str]) -> NodeBase | None:
        """Gets a compound node based on its '.' separated path"""
        compound = graph.findNode(paths[0])
        if compound is None:
            return None
        if len(paths)==1:
            return compound
        return self.get_function_compound(compound.rawGraph, paths[1:])


    def to_python(self,  # pylint: disable=unused-argument
                  exporter: 'PythonExporterImpl',
                  inpnames: list[str],  # pylint: disable=unused-argument
                  *args,
                  **kwargs):
        """Export Function node as pure python"""
        # export function definition
        node = self.get_function_compound(
            self.graph().graphManager.findRootGraph(),  # type: ignore # pylint: disable=not-callable
            self.getData('function').split('.')
        )
        if node is None:
            return
        node = cast('compound', node)
        if not exporter.is_node_function_processed(self):
            subexporter = exporter.__class__(node.rawGraph, # type: ignore
                                             exporter.converter_classes,
                                             1,
                                             exporter.exported_node_functions
                                            )
            exec_in_pins: list[PinBase] = [
                pin
                for pin
                in node.orderedInputs.values()
                if pin.isExec()
            ]
            if len(exec_in_pins)>0: # follow the flow fom first exec pin
                first_exec_pin = list(exec_in_pins[0].affects)[0]
                subexporter.export_from_pin(first_exec_pin)
            else: # no exec pin -> follow he flow back from output pins
                graph_output_nodes = cast(GraphBase, node.rawGraph) \
                    .getNodesList(classNameFilters=['graphOutputs'])
                for outnode in graph_output_nodes:
                    subexporter.process_node(outnode)
            for key, exp in subexporter.exported_node_functions.items():
                if key not in exporter.exported_node_functions:
                    exporter.set_node_function_processed(exp)
            for key, visited_node in subexporter.visited_nodes.items():
                if key not in exporter.visited_nodes:
                    exporter.set_node_processed(visited_node)
            exporter.add_imports(subexporter.get_imports_list())
            exporter.add_setups(subexporter.get_setups_list())
            in_pin_names = [pin.name
                            for pin
                            in node.orderedInputs.values()
                            if not pin.isExec()
                           ]
            exporter.add_sys_function(subexporter.get_sys_functions())
            exporter.add_function(subexporter.get_functions() +
                                  f"\ndef {node.name}({', '.join(in_pin_names)}):\n" +
                                  f"{subexporter.get_calls()}")
            exporter.set_node_function_processed(self)
        # export call
        exporter.add_call(f"{exporter.get_out_list(self, post=' = ')}{node.name}(" +
                          f"{', '.join(inpnames[1:])})\n")
        exporter.set_node_processed(self)
        if self.getPinSG('out', PinSelectionGroup.Outputs) is not None:
            exporter.call_named_pin(self, 'out')
                # TODO: this is an actual example not a generalized one
                # (could be multople which should be called from inside the exported function)


    def compute(self, *args, **kwargs):
        # get inputs
        compound = self.get_function_compound(
            self.graph().graphManager.findRootGraph(),# type: ignore # pylint: disable=not-callable
            self.getData('function').split('.')
        )
        rawGraph = GraphBase(self.name, self.graph().graphManager, self.graph()) # type: ignore # pylint: disable=not-callable
        rawGraph.populateFromJson(compound.rawGraph.serialize()) # copy # type: ignore

        graph_inputs_nodes = rawGraph.getNodesList(classNameFilters=['graphInputs'])

        for in_pin in self.orderedInputs.values():
            if in_pin.name != 'function':
                if not in_pin.isExec():
                    for node in graph_inputs_nodes:
                        if not (graph_in_pin:=cast(PinBase, cast(NodeBase, node)
                                     .getPinSG(in_pin.name,
                                               PinSelectionGroup.Outputs))) is None:
                            graph_in_pin.setData(self.getData(in_pin.name))

        for in_pin in self.orderedInputs.values():
            if in_pin.name != 'function':
                if in_pin.isExec():
                    for node in graph_inputs_nodes:
                        if not (graph_in_pin:=cast(PinBase, cast(NodeBase, node)
                                     .getPinSG(in_pin.name,
                                               PinSelectionGroup.Outputs))) is None:
                            graph_in_pin.call()

        graph_outputs_nodes = rawGraph.getNodesList(classNameFilters=['graphOutputs'])

        for out_pin in self.orderedOutputs.values():
            for node in graph_outputs_nodes:
                if not (graph_out_pin := cast(PinBase, cast(NodeBase, node)
                                             .getPinSG(out_pin.name,
                                                       PinSelectionGroup.Inputs))) is None:
                    self.setData(out_pin.name, graph_out_pin.getData())

        rawGraph.remove()
