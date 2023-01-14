from enum import Enum
from strenum import StrEnum
import time
from typing import Optional, Mapping
import logging

from qtpy.QtCore import QThread, QObject, Signal, Slot, QTimer
from qtpy.QtWidgets import QAction
from bluesky_queueserver_api.zmq import REManagerAPI
from bluesky_queueserver_api import BPlan

from haven import RunEngine


log = logging.getLogger()


class RunEngineAction(QAction):
    enabled_changed = Signal(bool)

    def setEnabled(self, new_state):
        super().setEnabled(new_state)
        self.enabled_changed.emit(new_state)


class REStates(StrEnum):
    """Possible states for a bluesky runengine."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"


class QueueClientThread(QThread):
    def __init__(self, *args, client, **kwargs):
        self.client = client
        super().__init__(*args, **kwargs)
        # Timer for polling the queueserver
        self.timer = QTimer()
        self.timer.timeout.connect(self.client.update_status)
        self.timer.start(1000)


class QueueClient(QObject):
    api: REManagerAPI
    _last_status: Optional[Mapping] = {}

    # Signals responding to queue changes
    status_changed = Signal(dict)

    def __init__(self, *args, api, **kwargs):
        self.api = api
        super().__init__(*args, **kwargs)

    def update_status(self):
        log.debug("Updating queue status.")
        status = self.api.status()
        if status != self._last_status:
            # Only update if the value has changed
            log.debug(f"Queue status update: {status}")
            self.status_changed.emit(status)
        self._last_status = status

    @Slot(bool)
    def request_pause(self, defer: bool = True):
        """Ask the queueserver run engine to pause.
        
        Parameters
        ==========
        defer
          If true, the run engine will be paused at the next
          checkpoint. Otherwise, it will pause now.

        """
        option = "deferred" if defer else "immediate"
        self.api.re_pause(option=option)

    @Slot(object)
    def add_queue_item(self, item):
        log.info(f"Client adding item to queue: {item}")
        result = self.api.item_add(item=item)
        if result['success']:
            log.info(f"Item added. New queue length: {result['qsize']}")
            self.update_status()
        else:
            log.error(f"Did not add queue item to queue: {result}")
            raise RuntimeError(result)

    @Slot()
    def start_queue(self):
        self.api.queue_start()

    @Slot()
    def resume_runengine(self):
        self.api.re_resume()

    @Slot()
    def stop_runengine(self):
        self.api.queue_stop()
        self.api.re_stop()

    @Slot()
    def abort_runengine(self):
        self.api.queue_stop()
        self.api.re_abort()

    @Slot()
    def halt_runengine(self):
        self.api.queue_stop()
        self.api.re_halt()
