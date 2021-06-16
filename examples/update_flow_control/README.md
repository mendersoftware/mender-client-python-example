# mender-client-python-example

## Overview

This example shows how to control the Update flow of the Mender client using the
D-Bus API.

At start time, it sets an Update Control Map that instructs the Mender client to
"pause" on every possible state. These are `ArtifactInstall_Enter`,
`ArtifactReboot_Enter`, and `ArtifactCommit_Enter`. Learn more about the Mender
client states in the [states
section](https://docs.mender.io/overview/state-script#states) from Mender
Docs.[States section from Mender Docs.

Then the application waits for user input. The user can select a new Update
Control Map to send to the Mender client. Each of the Update Control Map can
override the previously set maps, and in this way force continue any ongoing
update.

The code uses the Mender D-Bus API `io.mender.Update1` to set the Update Control
Map in the Mender client. Refer to Mender Docs for more details on the actual
[`io.mender.Update1.SetUpdateControlMap`
method](https://docs.mender.io/development/device-side-api/io.mender.update1#setupdatecontrolmap)
being used.

## Usage

See [main README](../../README.md) for instructions on how to install this
package. Once installed, start this example with:

```
mender-update-flow-control
```

Which initializes the application, sets all the states in the Update Control Map
to "pause", and asks the user for further input with the following prompt:

```
Current map is:
{
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
}
-----------------------
What do you want to do?
  0) Pause on all states
  1) Continue with Installing new software
  2) Continue with Rebooting
  3) Continue with Committing new software
  q) Quit

```

## Implementation

The example application implements two threads that communicate with two queues;
one thread is responsible for managing the Mender D-Bus API communication, and
another is responsible for dealing with the user input:

* `do_handle_update_control_map`: initializes the D-Bus communication with the
  Mender client, sets a "pause all" Update Control Map, and enters the main
  event loop. From this loop two events might happen: that a new map is received
  in the queue, or that the timeout from the current map is about to expire and
  the map needs refreshing. On D-Bus errors, the error message is reported in
  the corresponding queue and the thread exists.

* `do_main_interactive`: print the selection menu to the user and ask for what
  action to do next. When the user selects an action, the corresponding map is
  sent to the que for the D-Bus control thread to handle. It constantly
  refreshes the terminal to always display the current map on top of the user
  options menu. If a D-Bus error is received in the corresponding queue, the
  error message is printed to the user and the thread exists.

## Going to production

This example is meant to educate and show how the Mender D-Bus API works. There
are a few aspects that you need to take into consideration when writing a
production grade application based on this example.

### Selecting a UUID

This example uses a dummy [Universally Unique Identifier, or
UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier). Make sure to
choose a new random UUID for your application that will stay constant.

### Error handling and failure recovery

The code in this example just prints the message and exits on any D-Bus error. A
production application shall log the error but try to recover from it. Some of
the actions that can be taken are retrying at a later time, or reporting the
error to the user in a better way.

# Refreshing of the maps

The example constantly sets the "current" map. This is necessary for the Mender
client to keep the map active.

When a map expires it is not taken into account anymore for a Mender update and
by default the Mender client will continue on any step (assuming there no other
maps). This is a safety mechanism for the device to always be able to be updated
when a frontend process has crashed or is hanging.

The application can however customize what happens when a map expires using its
`on_map_expire` attribute in the map, which can be set to `continue`,
`force_continue`, or `fail`.

# Update Control Map priority

This example uses priority `-1` in all the maps being set. You may want to use a
different priority, or a combination of multiple priorities for different maps,
depending on your application.

When multiple Update Control Maps are active, the Mender client will merge them.
Higher priority maps always takes precedence; and when multiple maps exist for
the same priority, the order of precedence is `fail`, `pause`, `force_continue`,
The default action `continue` is only executed if no other action exists at any
priority level. The Mender client then applies the resulting Update Control Map.

Maps that are set using the Mender Web UI usually have priority `0`, unless the
deployment endpoint has been called manually to set a different priority.

# Update Control Map one-time action

Another interesting field in the map that is `on_action_executed`. In the
example application the map is setting "continue" in one of the states, which
takes effect for all future updates.

What `on_action_executed` does is to atomically execute the action of the map,
and then set the next action, so that you don't risk race conditions when
continuing an update and you want to pause the next update.

For example, with:

```
{
    "states": {
        "ArtifactInstall_Enter": {
            "action": "continue",
            "on_action_executed": "pause"
        },
    },
    "id": "01234567-89ab-cdef-0123-456789abcdef"
}
```

you don't need to set a new map to reinstate a pause. This is the official
recommendation.

### Note on Python multi-threading

Python (or more specifically, the CPython) does not support concurrent
multi-threading. Read more information about it in [threading module
documentation](https://docs.python.org/3/library/threading.html) and the [Python
glossary](https://docs.python.org/3/glossary.html#term-global-interpreter-lock).
If you are planning to use Python in production, consider using [multiprocessing
module](https://docs.python.org/3/library/multiprocessing.html) instead.

## Troubleshooting

If the application is not working, make sure of the following:
* `dbus-daemon` is running in your system
* Mender client is 2.7.0 or newer
* `D-Bus` APIs are enabled in the Mender client (they are enabled by default)
* The `io.mender.UpdateManager.conf` DBus policy file is installed in your system
  (typically at `/usr/share/dbus-1/system.d/` and has the right privileges set.

### ServiceUnknown error

The following error indicates that the Mender client is not running, or that the
version running does not support `UpdateManager` DBus API. Double-check the
checklist above.

```
ERROR: g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown: The name io.mender.UpdateManager was not provided by any .service files (2)
```

### AccessDenied error

The following error indicates that the user running the example does not have
enough privileges to query Mender client via DBus. By default, the Mender DBus
APIs are only available for root user. Run the application with `sudo` or modify
the DBus policy file.

```
ERROR: g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.AccessDenied: Rejected send message, 1 matched rules; type="method_call", sender=":1.39" (uid=1000 pid=20179 comm="/usr/bin/python3 /usr/local/bin/mender-update-flow") interface="org.freedesktop.DBus.Introspectable" member="Introspect" error name="(unset)" requested_reply="0" destination="io.mender.UpdateManager" (uid=0 pid=19880 comm="/usr/bin/mender daemon ") (9)
```
