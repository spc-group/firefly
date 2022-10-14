from pydm.main_window import PyDMMainWindow
# from qtpy.QtCore import Slot
from qtpy import QtCore, QtGui, QtWidgets


class FireflyMainWindow(PyDMMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customize_ui()
        self.export_actions()

    def add_menu_action(self, action_name: str, text: str, menu: QtWidgets.QMenu):
        """Add a new QAction to a menubar menu.

        The action triggers when the menu item is activated.

        Parameters
        ==========
        action_name
          The name of the parameter to the save the action. Will be
          accessible via *action_name* on the window, and window.ui.
        text
          Human-readable text to show on the menu item.
        menu
          The QMenu object in which to put this menu item.

        Returns
        =======
        action
          A QAction for the menu item.

        """
        action = QtWidgets.QAction(self)
        action.setObjectName(action_name)
        action.setText(text)
        menu.addAction(action)
        # Save the action as object parameters
        setattr(self.ui, action_name, action)
        setattr(self, action_name, action)
        return action

    def customize_ui(self):
        # Log viewer window
        # XAFS scan window
        self.add_menu_action(
            action_name="actionShow_Log_Viewer",
            text="Logs",
            menu=self.ui.menuView)
        # Scans menu
        self.ui.menuScans = QtWidgets.QMenu(self.ui.menubar)
        self.ui.menuScans.setObjectName("menuScans")
        self.ui.menuScans.setTitle("Scans")
        self.ui.menubar.addAction(self.ui.menuScans.menuAction())
        # XAFS scan window
        self.add_menu_action(
            action_name="actionShow_Xafs_Scan",
            text="XAFS Scan",
            menu=self.ui.menuScans)
        # Detectors menu
        self.ui.menuDetectors = QtWidgets.QMenu(self.ui.menubar)
        self.ui.menuDetectors.setObjectName("menuDetectors")
        self.ui.menuDetectors.setTitle("Detectors")
        self.ui.menubar.addAction(self.ui.menuDetectors.menuAction())        
        # Voltmeters window
        self.add_menu_action(
            action_name="actionShow_Voltmeters",
            text="Ion Chambers",
            menu=self.ui.menuDetectors)
    
    def export_actions(self):
        """Expose specific signals that might be useful for responding to window changes."""
        self.actionShow_Log_Viewer = self.ui.actionShow_Log_Viewer
        self.actionShow_Xafs_Scan = self.ui.actionShow_Xafs_Scan
        self.actionShow_Voltmeters = self.ui.actionShow_Voltmeters