import time
import pytest

from firefly.main_window import FireflyMainWindow, PlanMainWindow
from firefly.queue_client import REStates
from firefly.application import FireflyApplication


def test_navbar(qapp):
    window = PlanMainWindow()
    # Check navbar actions on the app
    assert hasattr(qapp, 'pause_runengine_action')
    # Check that the navbar actions are set up properly
    assert hasattr(window.ui, "navbar")
    navbar = window.ui.navbar
    # Navigation actions are removed
    assert window.ui.actionHome not in navbar.actions()
    # Run engine actions have been added to the navbar
    assert qapp.pause_runengine_action in navbar.actions()
    assert qapp.start_queue_action in navbar.actions()


def test_navbar_autohide(qapp, qtbot):
    """Test that the queue navbar is only visible when plans are queued."""
    window = PlanMainWindow()
    window.show()
    navbar = window.ui.navbar
    # Pretend the queue has some things in it
    status = {
        "items_in_queue": 3,
        "re_state": REStates.IDLE
    }
    with qtbot.waitSignal(qapp.queue_status_changed):
        qapp.queue_status_changed.emit(status)
    assert navbar.isVisible()
    # Make the queue be empty
    status["items_in_queue"] = 0
    with qtbot.waitSignal(qapp.queue_status_changed):
        qapp.queue_status_changed.emit(status)
    assert not navbar.isVisible()


@pytest.mark.xfail
def test_navbar_button_visibility(qapp, qtbot):
    """Test that the queue navbar only shows certain buttons at certain times."""
    window = PlanMainWindow()
    window.show()
    navbar = window.ui.navbar
    # Pretend the queue has some things in it
    status = {
        "re_state": REStates.RUNNING,
        "items_in_queue": 0,
    }
    with qtbot.waitSignal(qapp.queue_status_changed):
        qapp.queue_status_changed.emit(status)
    # Check that the right actions were toggled on and off
    actions = [ac.objectName() for ac in navbar.actions()]
    assert "pause_runengine_action" in actions
    assert "start_queue_action" not in actions
    assert "resume_queue_action" not in actions
    # Pretend the run engine has paused
    status["re_state"] = REStates.PAUSED
    with qtbot.waitSignal(qapp.queue_status_changed):
        qapp.queue_status_changed.emit(status)
    # Check that the right actions were toggled on and off
    actions = [ac.objectName() for ac in navbar.actions()]
    assert "pause_runengine_action" not in actions
    assert "start_queue_action" not in actions
    assert "resume_runengine_action" in actions


def test_add_menu_action(qapp):
    window = FireflyMainWindow()
    # Check that it's not set up with the right menu yet
    assert not hasattr(window, "actionMake_Salad")
    # Add a menu item
    action = window.add_menu_action(action_name="actionMake_Salad",
                                    text="Make Salad", menu=window.ui.menuTools)
    assert hasattr(window.ui, "actionMake_Salad")
    assert hasattr(window, "actionMake_Salad")    
    assert action.text() == "Make Salad"
    assert action.objectName() == "actionMake_Salad"


def test_customize_ui(qapp):
    window = FireflyMainWindow()
    assert hasattr(window.ui, "menuScans")
