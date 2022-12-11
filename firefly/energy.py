from qtpy import QtWidgets

from firefly import display


class XafsScanDisplay(display.FireflyDisplay):
    def customize_ui(self):
        pass

    def ui_filename(self):
        return "energy.ui"
