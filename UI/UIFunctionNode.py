"""The UI handling of the Function node"""  # pylint: disable=invalid-name

from PyFlow.UI.Canvas.UICommon import Colors
from PyFlow.UI.Canvas.UINodeBase import UINodeBase


class UIFunctionNode(UINodeBase):
    """UI of the Function node"""

    def __init__(self, raw_node, w=80, color=Colors.NodeBackgrounds, headColorOverride=None):
        super().__init__(raw_node, w, color, headColorOverride)

        self._rawNode.pinExposed.connect(self._createUIPinWrapper)
