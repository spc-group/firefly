from firefly.queue_client import REStates


def test_runengine_action_states(qapp, qtbot):
    """Check that the right runengine states are en/disabled."""
    # Pretend the queue is running
    new_status = {
        "items_in_queue": 0,
        "re_state": REStates.RUNNING,
    }
    with qtbot.waitSignal(qapp.queue_status_changed):
        qapp.queue_status_changed.emit(new_status)
    assert not qapp.start_queue_action.isEnabled()
