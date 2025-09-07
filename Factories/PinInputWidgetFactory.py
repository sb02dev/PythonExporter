"""Pin input widgets for the data nodes"""

from typing import cast
from PyFlow.Core import PinBase, NodeBase, GraphBase
from PyFlow.Core.Common import DEFAULT_WIDGET_VARIANT
from PyFlow.UI.Widgets.InputWidgets import InputWidgetSingle
from PyFlow.UI.Widgets.EnumComboBox import EnumComboBox

class CompoundNamesWidget(InputWidgetSingle):
    """A dropdown selector with all compound names"""
    def __init__(self, parent=None, dataSetCallback=None, defaultValue=None, **kwargs):
        super().__init__(parent, dataSetCallback, defaultValue, **kwargs)
        pin = cast(PinBase, self.dataSetCallback.__self__)  # type: ignore
        graph = cast(NodeBase, pin.owningNode()).graph()  # type: ignore
        names = self.getCompoundNames(graph.graphManager.findRootGraph())
        self.enumbox = EnumComboBox(names)
        self.setWidget(self.enumbox)
        self.enumbox.changeCallback.connect(self.dataSetCallback)

    def blockWidgetSignals(self, bLock=False):
        return self.enumbox.blockSignals(bLock)

    def setWidgetValue(self, value):
        self.enumbox.setCurrentText(value)

    def getCompoundNames(self, graph: GraphBase, prefix = ''):  # pylint: disable=invalid-name
        """Find all the compound names in the graph"""
        compounds = graph.getNodesList(classNameFilters=['compound'])
        result = []
        for c in compounds:
            result.append(f"{'' if prefix=='' else prefix+'.'}{c.name}")
            result.extend(self.getCompoundNames(c.rawGraph, result[-1]))
        return result


def getInputWidget(dataType, dataSetter, defaultValue,  # pylint: disable=invalid-name
                   widgetVariant=DEFAULT_WIDGET_VARIANT, **kwargs):  # pylint: disable=invalid-name
    """Returns the input widget variants defined above"""
    if dataType=='StringPin':
        if widgetVariant == 'CompoundNamesWidget':
            return CompoundNamesWidget(dataSetCallback=dataSetter,
                                       defaultValue=defaultValue,
                                       **kwargs)
