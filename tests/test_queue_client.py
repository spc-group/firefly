import time
import pytest
from unittest.mock import MagicMock
import asyncio

from bluesky import RunEngine, plans as bp
from qtpy.QtCore import QThread
from qtpy.QtTest import QSignalSpy
from bluesky_queueserver_api.zmq import REManagerAPI

from firefly.queue_client import QueueClient
from firefly.application import REManagerAPI
from firefly.main_window import FireflyMainWindow


def test_setup(qapp):
    api = MagicMock()
    FireflyMainWindow()
    qapp.prepare_queue_client(api=api)
    assert hasattr(qapp, "pause_runengine_action")
    assert (
        qapp.pause_runengine_action.toolTip() == "Pause run-engine at next checkpoint."
    )


def test_queue_re_control(qapp):
    """Test if the run engine can be controlled from the queue client."""
    api = MagicMock()
    qapp.prepare_queue_client(api=api)
    window = FireflyMainWindow()
    window.show()
    # Try and pause the run engine
    qapp.pause_runengine_action.trigger()
    # Check if the API paused
    time.sleep(0.1)
    api.re_pause.assert_called_once_with(option="deferred")
    # Pause the run engine now!
    api.reset_mock()
    qapp.pause_runengine_now_action.trigger()
    # Check if the API paused now
    time.sleep(0.1)
    api.re_pause.assert_called_once_with(option="immediate")
    # Start the queue
    api.reset_mock()
    qapp.start_queue_action.trigger()
    # Check if the queue started
    time.sleep(0.1)
    api.queue_start.assert_called_once()
    # Resume the queue
    api.reset_mock()
    qapp.resume_runengine_action.trigger()
    # Check if the API resumed
    time.sleep(0.1)
    api.re_resume.assert_called_once_with()
    # Stop the queue
    api.reset_mock()
    qapp.stop_runengine_action.trigger()
    # Check if the API stopped
    time.sleep(0.1)
    api.re_stop.assert_called_once_with()
    api.queue_stop.assert_called_once_with()
    # Halt the queue
    api.reset_mock()
    qapp.halt_runengine_action.trigger()
    # Check if the API halted
    time.sleep(0.1)
    api.re_halt.assert_called_once_with()
    # Abort the queue
    api.reset_mock()
    qapp.abort_runengine_action.trigger()
    # Check if the API aborted
    time.sleep(0.1)
    api.re_abort.assert_called_once_with()


def test_run_plan(qapp, qtbot):
    """Test if a plan can be queued in the queueserver."""
    FireflyMainWindow()
    api = MagicMock()
    api.item_add.return_value = {"success": True, "qsize": 2}
    qapp.prepare_queue_client(api=api)
    # Send a plan
    with qtbot.waitSignal(
        qapp.queue_length_changed, timeout=1000, check_params_cb=lambda l: l == 2
    ):
        qapp.queue_item_added.emit({})
    # Check if the API sent it
    api.item_add.assert_called_once_with(item={})


def test_check_status(qapp, qtbot):
    FireflyMainWindow()
    api = MagicMock()
    qapp.prepare_queue_client(api=api)
    # Check that the queue length is changed
    status = {
        "msg": "RE Manager v0.0.18",
        "items_in_queue": 0,
        "items_in_history": 0,
        "running_item_uid": None,
        "manager_state": "idle",
        "queue_stop_pending": False,
        "worker_environment_exists": True,
        "worker_environment_state": "idle",
        "worker_background_tasks": 0,
        "re_state": "idle",
        "pause_pending": False,
        "run_list_uid": "daaa454b-fdfb-42ca-82aa-63c837758907",
        "plan_queue_uid": "6918a069-260d-450c-8651-a27cab9b8b4e",
        "plan_history_uid": "b7b2f0fb-2436-4788-be97-8bd4cd7ef5a1",
        "devices_existing_uid": "f8f871bd-191b-419e-ab87-267799d82fb3",
        "plans_existing_uid": "a1e9c70e-35ba-4ed4-9e77-b41a65f92c4f",
        "devices_allowed_uid": "c5c56cac-99b4-46c1-ba0b-912276672fb9",
        "plans_allowed_uid": "46218e65-58f1-47a4-8af5-119c642e59f7",
        "plan_queue_mode": {"loop": False},
        "task_results_uid": "88611cc8-f40c-4f5a-bb04-31d09c6ea1c5",
        "lock_info_uid": "7bfd8a21-dae3-419d-8e1c-0345566dd7cf",
        "lock": {"environment": False, "queue": False},
    }
    api.status.return_value = status
    qapp.pause_runengine_action.setEnabled(True)
    qapp.pause_runengine_action.setEnabled(False)
    qapp.pause_runengine_action.setDisabled(False)
    qapp.pause_runengine_action.setDisabled(True)
    time.sleep(0.1)
    with qtbot.waitSignal(
        qapp.queue_status_changed, timeout=1000, check_params_cb=lambda d: d == status
    ):
        qapp._queue_client.update_status()
    # Check that it isn't emitted a second time
    with qtbot.assertNotEmitted(qapp.queue_status_changed):
        qapp._queue_client.update_status()
