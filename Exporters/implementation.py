"""Implementation module of PyFlow graph exporter into pure Python scripts"""
from typing import Callable, Iterator, Optional

from PyFlow.Core import PinBase, GraphBase, NodeBase
from PyFlow.Core.Common import PinSelectionGroup


class PythonExporterImpl:
    """Implementation class of pure Python export"""

    def __init__(self,
                 graph: GraphBase,
                 converter_classes: list[object],
                 indent = 0,
                 exported_node_functions: Optional[dict] = None):
        self._graph = graph
        self._visited_nodes = {}
        self._exported_node_functions = {} if exported_node_functions is None \
                                        else exported_node_functions
        self._imports: list[str|tuple[str,str|None]|tuple[str,list[str]]] = []
        self._setups: dict[str, str] = {}
        self._variables = "VARS = {}\n"
        self._sys_function_part = ""
        self._function_part = ""
        self._calling_part = ""
        self._indent = indent
        self._converter_classes = converter_classes


    ################################
    ###        PROCESSING        ###
    ################################
    def export_from_pin(self, pin: PinBase):
        """Export part of the graph which starts with this Exec Pin"""
        if not pin.isExec():
            return

        # get the owning node
        owning_node: NodeBase | None = pin.owningNode()
        if not isinstance(owning_node, NodeBase):
            return
        if owning_node.__class__.__name__=="graphInputs":
            # add the input parameters in _variables
            for parampin in owning_node.orderedOutputs.values():
                if not parampin.isExec():
                    self.add_variable(parampin.name, repr(parampin.currentData()))
            # start with the node where the exec pin points
            if len(pin.affects)==0:
                return
            owning_node = list(pin.affects)[0].owningNode()

        # convert the graph
        self.process_node(owning_node)  # type: ignore


    def process_node(self, node: NodeBase, *args, **kwargs):
        """This is the gist of the converter: Process one PyFlow Node"""
        if self.is_node_processed(node):
            return

        # handle input pins
        allinpnames: list[str] = []
        allparnames: list[str] = []
        for inpin in node.orderedInputs.values():
            if not inpin.isExec():
                curparnames, curinpnames = self.process_pin(inpin)
                allparnames.extend(curparnames)
                allinpnames.extend(curinpnames)

        # handle the current node and follow its exec pins
        if self.is_node_processed(node):
            # check the node again if processed (it could be processed in
            # the previous steps)
            return

        self.convert_node(node, allparnames, allinpnames, *args, **kwargs)


    def process_pin(self, pin: PinBase) -> tuple[list, list]:
        """Processes one pin.
        
        Returns:
            tuple:
                list: list of parameter names extracted from the pin
                list: list of the input names extracted from the pin
        """
        parnames: list[str] = []
        inpnames: list[str] = []
        # convert the inputs and its sources
        # TODO: multiple connections
        parnames.append(pin.name)
        if len(list(pin.affected_by))==0:
            # pin is holding a constant value
            if pin.dataType=='StringPin':
                inpnames.append(f"{repr(str(pin.currentData()))}")
            elif pin.dataType in ['BoolPin', 'FloatPin', 'IntPin']:
                inpnames.append(f"{str(pin.currentData())}")
            # TODO: handle other data types
        else:
            # pin is connected to an input -> we find the full name of the
            # `affected_by` pins
            inpnames.extend(
                [
                    affpin.name if affpin.owningNode().__class__.__name__=="graphInputs"
                    else affpin.getFullName()
                    for affpin in list(pin.affected_by)
                ]
            )
            _inpnodes = [affpin.owningNode() for affpin in list(pin.affected_by)]
            # check if they were already exported and process them as neccessary
            for inpnode in _inpnodes:
                if not self.is_node_processed(inpnode) and \
                        inpnode.__class__.__name__!="graphInputs":
                    self.process_node(inpnode)

        return parnames, inpnames


    def convert_node(self,
                     node: NodeBase,
                     parnames: list[str],
                     inpnames: list[str],
                     *args,
                     **kwargs):
        """Do the actual conversion of one Node to Python"""
        if hasattr(node, 'to_python'):
            # node has a full way to convert
            for pin in node.to_python(self, inpnames, *args, *kwargs):  # type: ignore
                # TODO: consider instead of this yielding mechanism, directly calling
                # exporter.call_named_pin() from the handlers
                self.call_named_pin(node, pin)
        elif (method := self.get_converter_method(node.__class__.__name__)) is not None:
            # we have a full way in our converter class to convert
            for pin in method(
                    self, node, inpnames, *args, **kwargs):
                self.call_named_pin(node, pin)
        else:
            # we will convert ourselves with drop-ins for each part (if exists)
            if not self.is_node_function_processed(node):
                self.process_node_function(node, parnames, inpnames, *args, **kwargs)
            self.process_node_calling(node, parnames, inpnames, *args, **kwargs)
            # call exec pins
            opins: Iterator[PinBase] = (pin for pin in node.orderedOutputs.values() if pin.isExec())
            for opin in opins:
                self.call_named_pin(node, opin.name)


    def call_named_pin(self, node: NodeBase, pinname: str):
        """Follows the export with an exec pin by its name"""
        pin = node.getPinSG(pinname, PinSelectionGroup.Outputs)
        if pin is None:
            print(node, pinname, "not found")
            return
        for cpin in list(pin.affects):
            self.export_from_pin(cpin)


    def process_node_function(self,
                              node: NodeBase,
                              parnames: list[str],
                              inpnames: list[str],
                              *args,
                              **kwargs):  # pylint: disable=unused-argument
        """Converts the function part of a node"""
        fun_str = f"def {node.__class__.__name__}({', '.join(parnames)}):\n"
        if hasattr(node, 'python_func'):
            # we have a function which returns function definition string
            fun_str += node.python_func(self, *args, **kwargs)  # type: ignore
        elif (method := self.get_converter_method("func_"+node.__class__.__name__)) is not None:
            fun_str += method(self, node, *args, **kwargs)
        else:
            fun_str = None
        if fun_str:
            self.add_sys_function(fun_str)
        self.set_node_function_processed(node)


    def process_node_calling(self,
                             node: NodeBase,
                             parnames: list[str],
                             inpnames: list[str],
                             *args,
                             **kwargs):  # pylint: disable=unused-argument
        """Converts the call of a node"""
        if hasattr(node, 'python_call'):
            self.add_call(node.python_call(self, inpnames, *args, **kwargs)) # type: ignore
        elif (method := self.get_converter_method("call_"+node.__class__.__name__)) is not None:
            self.add_call(method(self, node, inpnames, *args, **kwargs))
        else:
            self.add_call(
                f"{self.get_indent_str()}{self.get_out_list(node, post=' = ')}" +
                f"{node.__class__.__name__}({', '.join(inpnames)})"
            )
        self.set_node_processed(node)


    def get_out_list(self, node: NodeBase, post='') -> str:
        """Gets an output list as an str (the left hand side of the
        calling statement)
        """
        lst = ', '.join([opin.getFullName()
                         for opin in node.orderedOutputs.values()
                         if not opin.isExec()])
        return '' if lst=='' else lst+post


    def collect_subexporter_results(self, subexporter: "PythonExporterImpl", node: NodeBase):
        """Collects all the results from a subexporter and updates our
        status accordingly"""
        for key, exp in subexporter.exported_node_functions.items():
            if key not in self._exported_node_functions:
                self._exported_node_functions[key] = exp
        for key, n in subexporter.visited_nodes.items():
            if key not in self._visited_nodes:
                self._visited_nodes[key] = n
        self.add_imports(subexporter.get_imports_list())
        self.add_setups(subexporter.get_setups_list())
        self.add_sys_function(subexporter.get_sys_functions())
        self.add_function(subexporter.get_functions())
        inpinnames = [pin.name
                      for pin in node.orderedInputs.values()
                      if not pin.isExec()]
        self.add_function(f"def {node.name}({', '.join(inpinnames)}):\n{subexporter.get_calls()}")



    ################################
    ### STATUS HELPERS/ACCESSORS ###
    ################################
    # private list accessors
    @property
    def converter_classes(self):
        """Read-only accessor to our converter classes list"""
        return self._converter_classes

    # node processing status accessors
    def is_node_processed(self, node: NodeBase) -> bool:
        """Returns true if the node was already processed during the export"""
        return node.path() in self._visited_nodes

    def set_node_processed(self, node: NodeBase):
        """Sets the node as processed"""
        # TODO: actually we could be only sure that from this exec pin (if we are not pure)
        # we are visited. even more from this connection of this exec pin (because multiple
        # connections would need the call part to be repeated). maybe we should change this
        # to nodes-visited-from-pin-through-pin dictionary...
        self._visited_nodes[node.path()] = node

    @property
    def visited_nodes(self):
        """Read-only accessor to our list of already visited nodes"""
        return self._visited_nodes

    def is_node_function_processed(self, node: NodeBase) -> bool:
        """Returns true if the node's function was already processed during the export"""
        if node.__class__.__name__=='FunctionNode':
            return 'FunctionNode_'+node.getData('function') in self._exported_node_functions
        return node.__class__.__name__ in self._exported_node_functions

    def set_node_function_processed(self, node: NodeBase):
        """Sets the node as its function is processed"""
        if node.__class__.__name__ == 'FunctionNode':
            self._exported_node_functions['FunctionNode_'+node.getData('function')] = node
        else:
            self._exported_node_functions[node.__class__.__name__] = node

    @property
    def exported_node_functions(self):
        """Read-only accessor to our list of already exported node functions"""
        return self._exported_node_functions


    # import code-part accessors
    def add_import(self,
                   module_name: str,
                   alias: Optional[str]=None,
                   imports: Optional[list[str]]=None):
        """Adds an import to the list, aggregating with existing ones if neccessary.

        Examples:
            add_import("pandas", alias="pd") --> import pandas as pd
            add_import("os") --> import os

        Multiple import examples:
            add_import("sqlalchemy", imports=["create_engine", "URL"])
            add_import("sqlalchemy", imports=["text"])

            from sqlalchemy import (
                create_engine,
                URL,
                text
            )


        Args:
            module_name (str): the module to import (from)
            alias (str, optional): an optional alias for the module
                                   (ignored if `imports` is provided)
            imports (str[], optional): a list of the imports from the
                                       given module 
        """
        if alias is None and imports is None:
            # import <module_name>
            for imp in self._imports:
                if isinstance(imp, str):
                    if imp==module_name:
                        return
            self._imports.append(module_name)
            return

        if imports is None:
            # import <module_name> as <alias>
            # stored as a tuple of (str, str)
            for imp in self._imports:
                if isinstance(imp, tuple) and \
                   isinstance(imp[0], str) and isinstance(imp[1], str):
                    if imp[0]==module_name and imp[1]==alias:
                        return
            self._imports.append((module_name, alias))
            return

        # from <module_name> import (stuff1, stuff2)
        # stored as a tuple of (str, list)
        for imp in self._imports:
            if isinstance(imp, tuple) and \
               isinstance(imp[0], str) and isinstance(imp[1], list):
                if imp[0]==module_name:
                    for to_import in imports:
                        if not to_import in imp[1]:
                            imp[1].append(to_import)
                    return
        self._imports.append((module_name, imports))

    def add_imports(self,
                    imports: list[str |tuple[str, str|None]|tuple[str, list[str]]]):
        """Adds the given imports to this exporter, eliminating duplicates
        
        Args:
            imports: the imports to add (typically from a subexporter)
        """
        for imp in imports:
            if isinstance(imp, str):
                self.add_import(imp)
            elif isinstance(imp[1], str):
                self.add_import(imp[0], alias=imp[1])
            else:
                self.add_import(imp[0], imports=imp[1])


    def get_imports_list(self):
        """Read-only accessor to the imports list of this exporter"""
        return self._imports


    def get_imports(self):
        """Gets the imports code-part calculated on the fly from _imports list"""
        prg=""
        for imp in self._imports:
            if isinstance(imp, str):
                prg+=f"import {imp}\n"
            elif isinstance(imp[1], str):
                prg+=f"import {imp[0]} as {imp[1]}\n"
            elif isinstance(imp[1], list):
                prg_part=f"from {imp[0]} import ("
                prg+=f"{prg_part}{(f',{chr(10)}'+' '*len(prg_part)).join(imp[1])}){chr(10)}"
        while len(prg)>0 and prg[-1] == '\n':
            prg = prg[:-1]
        return prg


    # variable code-part accessors
    def add_variable(self, varname: str, valuestr: str):
        """Add a new variable to the top of the script"""
        self._variables += f"{self.get_indent_str()}{varname} = {valuestr}\n"


    def get_variables(self):
        """A read-only accessor to our variable definition string"""
        return self._variables


    # setup code-part accessors
    def add_setup(self, setup_id: str, prg: str, indent_first: bool = False):
        """Add a setup program part (with an id), if the id is
        already added doesn't overwrite.
        
        Args:
            setup_id (str): the id of the setup program part (this is used
                            only to recognize possible duplications)
            prg (str): the Python program code as a string
        """
        if setup_id in self._setups:
            return
        if indent_first:
            prg = self.indent_text(prg)
        self._setups[setup_id] = prg


    def add_setups(self, setups: dict[str, str]):
        """Add multiple setup parts at once (typically from subexporter)
        eliminating duplicates
        
        Args:
            setups (dict[str, str]): a dictionary of setups key is 'deduplicating' id
                                     value is the program part
        """
        for setup_id, prg in setups.items():
            self.add_setup(setup_id, prg)


    def get_setups_list(self):
        """Read-only accessor to the setups list of this exporter"""
        return self._setups


    def get_setups(self) -> str:
        """Return the setup parts compiled into a single string to use
        in the final Python code
        
        Returns:
            str: the compiled program part as a string
        """
        return '\n'.join(self._setups.values())


    # system function code-part accessors
    def add_sys_function(self, sys_func_str: str, indent_first: bool = False):
        """Add statements to the system functions code-part"""
        if indent_first:
            sys_func_str = self.indent_text(sys_func_str)
        self._sys_function_part += f"{sys_func_str}\n\n"


    def get_sys_functions(self):
        """A read-only accessor to our system functions code-part string"""
        return self._sys_function_part


    # function code-part accessors
    def add_function(self, func_str: str, indent_first: bool = False):
        """Add statements to the functions code-part"""
        if indent_first:
            func_str = self.indent_text(func_str)
        self._function_part += f"{func_str}\n"


    def get_functions(self):
        """A read-only accessor to our functions code-part string"""
        return self._function_part


    # main code-part accessors
    def increase_indent(self, by: int = 1):
        """Increases the indent for the following add_call commands"""
        self._indent += by

    def decrease_indent(self, by: int = 1):
        """Increases the indent for the following add_call commands"""
        self._indent -= by


    def add_call(self, call_str: str, indent_first: bool = True):
        """Add statements to the call code-part"""
        if call_str=='':
            return
        if indent_first:
            call_str = self.indent_text(call_str)
        self._calling_part += f"{call_str}\n"


    def get_calls(self):
        """A read-only accessor to our main program part string"""
        call = self._calling_part
        while len(call)>0 and call[-1] == '\n':
            call = call[:-1]

        return call


    ################################
    ###     GENERAL HELPERS      ###
    ################################
    # helpers
    def get_indent_str(self):
        """Get an indentation string from the current number of indents"""
        return '    '*self._indent


    def indent_text(self, text: str) -> str:
        """Indent the given text with our current number of indents"""
        ind = self.get_indent_str()
        return '\n'.join(ind+line for line in text.splitlines())

    def get_converter_method(self, name: str) -> Optional[Callable]:
        """Get a converter method by name from all of the loaded
        converters or None if not found"""
        for converter in self._converter_classes:
            if hasattr(converter, name):
                return getattr(converter, name)
        return None
