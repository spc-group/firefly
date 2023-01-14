import subprocess
from pathlib import Path
from typing import Sequence

from qtpy import QtWidgets, QtCore
from pydm import Display

from .queue_client import REStates


class FireflyDisplay(Display):
    caqtdm_ui_file: str = ""
    caqtdm_command: str = "/APSshare/bin/caQtDM -style plastique -noMsg"
    # Styles for controls in various states
    plan_buttons: Sequence = []
    _runengine_state: REStates = REStates.IDLE
    _queue_length: int = 0
    queue_plan_button_style = {
        "background-color": "rgb(0, 123, 255)",
        "color": "white",
        "border-color": "rgb(0, 123, 255)",
    }
    run_plan_button_style = {
        "background-color": "rgb(40, 167, 69)",
        "color": "white",
        "border-color": "rgb(40, 167, 69)",
    }
        
    def __init__(self, parent=None, args=None, macros=None, ui_filename=None, **kwargs):
        super().__init__(parent=parent, args=args, macros=macros, ui_filename=ui_filename, **kwargs)
        self.customize_device()
        self.customize_ui()
        # Handlers for changing the button styles based on runengine state
        app = QtWidgets.QApplication.instance()
        app.queue_status_changed.connect(self.update_button_styles)

    def update_button_styles(self, status):
        # Determine which stylesheet to use
        is_idle = status['re_state'] == REStates.IDLE
        has_queue = status['items_in_queue'] > 0
        if is_idle and not has_queue:
            new_style = self.run_plan_button_style
        else:
            new_style = self.queue_plan_button_style
        # Apply the style to the relevant buttons
        for btn_name in self.plan_buttons:
            # Get the old style
            btn = getattr(self.ui, btn_name)
            style = btn.style()
            # Update some properties
            for key, val in new_style.items():
                style.setProperty(key, val)
            # Push the new style to the button
            btn.setStyle(style)

    def launch_caqtdm(self, macros={}, ui_file: str = None):
        """Launch a caQtDM window showing the window's panel."""
        if ui_file is None:
            ui_file = self.caqtdm_ui_file
        cmds = self.caqtdm_command.split()
        macro_str = ",".join(f"{key}={val}" for key, val in macros.items())
        cmds = [*cmds, "-macro", macro_str, ui_file]
        subprocess.Popen(cmds)

    def customize_device(self):
        pass

    def customize_ui(self):
        pass
    
    def ui_filename(self):
        raise NotImplementedError
    
    def ui_filepath(self):
        path_base = Path(__file__).parent
        return path_base / self.ui_filename()
