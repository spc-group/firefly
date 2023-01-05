from firefly.queue_client import REStates


def test_runengine_action_states(qapp, qtbot):
    """Check that the right runengine states are en/disabled."""
    # Pretend the queue is running
    with qtbot.waitSignal(qapp.runengine_state_changed):
        qapp.runengine_state_changed.emit(REStates.RUNNING)
    assert not qapp.start_queue_action.isEnabled()
