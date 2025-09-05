"""A pure Python exporter for PyFlow"""  # pylint: disable=invalid-name
import os
from typing import TYPE_CHECKING

import importlib.util
import inspect

from PyFlow.Core.PackageBase import PackageBase
# import the converter base from the PythonExporter package
try:
    from PyFlow.Packages.PythonExporter.Exporters.converter_base import (  # pylint: disable=import-error, no-name-in-module # type: ignore
        ConverterBase
    )
except ImportError:
    from .Exporters.converter_base import ConverterBase


class PythonExporter(PackageBase):
    """The main Package entry point"""
    def __init__(self):
        super(PythonExporter, self).__init__()
        try:
            self.analyzePackage(os.path.dirname(__file__), [  # type: ignore # pylint: disable=too-many-function-args
                ('Converters', ConverterBase)
            ])
        except TypeError:
            # fallback until analyzePackage gets the second argument
            # in `https://github.com/pedroCabrera/PyFlow`
            packagePath = os.path.dirname(__file__)
            self.analyzePackage(packagePath)

            # workaround (copied from PyFlow, but all Converter implementing
            # package would need these)
            def import_subclasses(directory, base_class):
                subclasses = []
                for filename in os.listdir(directory):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        module_name = "PyFlow.Packages."+self.__class__.__name__ + \
                            "."+os.path.basename(directory)+"."+filename[:-3]
                        file_path = os.path.join(directory, filename)
                        # Dynamically load the module
                        spec = importlib.util.spec_from_file_location(
                            module_name, file_path)
                        module = importlib.util.module_from_spec(spec)  # type: ignore
                        spec.loader.exec_module(module)  # type: ignore
                        for _, obj in inspect.getmembers(module, inspect.isclass):
                            # Ensure that the class is defined in this module to avoid
                            # imported classes from elsewhere
                            # if inspect.getmodule(obj) == None or \
                            #    inspect.getmodule(obj) == module:
                            if issubclass(obj, base_class) and obj is not base_class:
                                subclasses.append(obj)
                return subclasses

            def loadPackageElements(packagePath, element, elementDict, classType):
                packageFolders = os.listdir(packagePath)
                if element in packageFolders:
                    directory = os.path.join(packagePath, element)
                    found_subclasses = import_subclasses(directory, classType)
                    for subclass in found_subclasses:
                        elementDict[subclass.__name__] = subclass

            self._CONVERTERS = {}
            loadPackageElements(packagePath, 'Converters', self._CONVERTERS, ConverterBase)
