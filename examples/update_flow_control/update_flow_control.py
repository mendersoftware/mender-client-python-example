# Copyright 2021 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""example application to control the Update flow of the Mender client
"""

import os
import sys
import threading
from datetime import datetime, timedelta
from queue import Empty, SimpleQueue
from typing import Any, Tuple

from gi.repository.GLib import Error as DBusError  # type: ignore
from pydbus import SystemBus  # type: ignore

UPDATE_CONTROL_MAP_PAUSE_ALL = """{
	"priority": -1,
	"states": {
		"ArtifactInstall_Enter": {
			"action": "pause"
		},
		"ArtifactReboot_Enter": {
			"action": "pause"
		},
		"ArtifactCommit_Enter": {
			"action": "pause"
		}
	},
	"id": "01234567-89ab-cdef-0123-456789abcdef"
}"""

UPDATE_CONTROL_MAP_CONTINUE_INSTALL = """{
	"priority": -1,
	"states": {
		"ArtifactInstall_Enter": {
			"action": "continue"
		},
		"ArtifactReboot_Enter": {
			"action": "pause"
		},
		"ArtifactCommit_Enter": {
			"action": "pause"
		}
	},
	"id": "01234567-89ab-cdef-0123-456789abcdef"
}"""

UPDATE_CONTROL_MAP_CONTINUE_REBOOT = """{
	"priority": -1,
	"states": {
		"ArtifactInstall_Enter": {
			"action": "pause"
		},
		"ArtifactReboot_Enter": {
			"action": "continue"
		},
		"ArtifactCommit_Enter": {
			"action": "pause"
		}
	},
	"id": "01234567-89ab-cdef-0123-456789abcdef"
}"""

UPDATE_CONTROL_MAP_CONTINUE_COMMIT = """{
	"priority": -1,
	"states": {
		"ArtifactInstall_Enter": {
			"action": "pause"
		},
		"ArtifactReboot_Enter": {
			"action": "pause"
		},
		"ArtifactCommit_Enter": {
			"action": "continue"
		}
	},
	"id": "01234567-89ab-cdef-0123-456789abcdef"
}"""


# Queue to send maps from user to D-Bus thread
set_new_map_queue = SimpleQueue()  # type: SimpleQueue

# Queue to send error messages from D-Bus to user thread
dbus_error_queue = SimpleQueue()  # type: SimpleQueue


def clear_console():
    """Clear console. Use "clear" for Linux and "cls" for Windows."""
    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)


def ask(text: str) -> str:
    """Ask a question and return the reply."""

    sys.stdout.write(text)
    sys.stdout.flush()
    reply = sys.stdin.readline().strip()
    sys.stdout.write("\n")
    return reply


def set_update_control_map(
    io_mender_update1_object: Any, update_control_map: str
) -> Tuple[str, int]:
    """Set the given Update Control Map in Mender using D-Bus method
    io.mender.Update1.SetUpdateControlMap. Returns [error_msg,refresh_timeout]
    """
    try:
        refresh_timeout = io_mender_update1_object.SetUpdateControlMap(
            update_control_map
        )
    except DBusError as dbus_error:
        return dbus_error, 30

    if refresh_timeout == 0:
        err_msg = "io.mender.Update1.SetUpdateControlMap returned refresh_timeout=0"
        return err_msg, 30

    return "", refresh_timeout


def do_handle_update_control_map():
    """Manage D-Bus communication with the Mender client

    At start, initializes the proxy D-Bus object and sets a pause all Update
    Control Map. Then, it will wait either for an expire of the current map to
    just refresh it, or a new map coming from the queue to set that one instead.
    """

    # Get the D-Bus proxy object interface io.mender.Update1
    try:
        remote_object = SystemBus().get(
            bus_name="io.mender.UpdateManager", object_path="/io/mender/UpdateManager"
        )["io.mender.Update1"]
    except DBusError as dbus_error:
        dbus_error_queue.put(dbus_error)
        return

    # Initialize the Update Control Map for pause in all states
    err_msg, refresh_timeout = set_update_control_map(
        remote_object, UPDATE_CONTROL_MAP_PAUSE_ALL
    )
    if err_msg != "":
        dbus_error_queue.put(err_msg)
        return

    current_map = UPDATE_CONTROL_MAP_PAUSE_ALL
    next_refresh_at = datetime.now() + timedelta(0, refresh_timeout - 1)

    err_msg = ""
    while not err_msg:
        try:
            new_map = set_new_map_queue.get(timeout=0.2)
        except Empty:
            pass
        else:
            err_msg, refresh_timeout = set_update_control_map(remote_object, new_map)
            current_map = new_map
            next_refresh_at = datetime.now() + timedelta(0, refresh_timeout - 1)

        if next_refresh_at <= datetime.now():
            err_msg, refresh_timeout = set_update_control_map(
                remote_object, current_map
            )
            next_refresh_at = datetime.now() + timedelta(0, refresh_timeout - 1)

    # An error ocurred, report to the queue and exit
    dbus_error_queue.put(err_msg)


def do_main_interactive():
    """Interactively ask the user for input and apply the desired Update Control
    Map
    """

    # Wait up to 500ms for D-Bus errors from initialization
    try:
        dbus_err = dbus_error_queue.get(timeout=0.5)
    except Empty:
        pass
    else:
        print(f"ERROR: {dbus_err}")
        return

    current_map = UPDATE_CONTROL_MAP_PAUSE_ALL
    while True:
        clear_console()
        print("Current map is:")
        print(current_map)
        print("-----------------------")
        print("What do you want to do?")
        print("  0) Pause on all states")
        print("  1) Continue with Installing new software")
        print("  2) Continue with Rebooting")
        print("  3) Continue with Committing new software")
        print("  q) Quit")

        reply = ask("Choice? ")
        if reply.lower() == "q":
            return

        if reply == "0":
            set_new_map_queue.put(UPDATE_CONTROL_MAP_PAUSE_ALL)
            current_map = UPDATE_CONTROL_MAP_PAUSE_ALL
        elif reply == "1":
            set_new_map_queue.put(UPDATE_CONTROL_MAP_CONTINUE_INSTALL)
            current_map = UPDATE_CONTROL_MAP_CONTINUE_INSTALL
        elif reply == "2":
            set_new_map_queue.put(UPDATE_CONTROL_MAP_CONTINUE_REBOOT)
            current_map = UPDATE_CONTROL_MAP_CONTINUE_REBOOT
        elif reply == "3":
            set_new_map_queue.put(UPDATE_CONTROL_MAP_CONTINUE_COMMIT)
            current_map = UPDATE_CONTROL_MAP_CONTINUE_COMMIT
        else:
            print(f"Unknown option: {reply}")

        # Wait up to 500ms for D-Bus errors from setting the map
        try:
            dbus_err = dbus_error_queue.get(timeout=0.5)
        except Empty:
            pass
        else:
            print(f"ERROR: {dbus_err}")
            return


def main():
    """Entry point function: start one thread to handle the D-Bus interface and
    another to handle user input.
    """

    thread_main = threading.Thread(target=do_main_interactive)
    thread_dbus = threading.Thread(target=do_handle_update_control_map)
    thread_dbus.daemon = True

    thread_main.start()
    thread_dbus.start()

    thread_main.join()
