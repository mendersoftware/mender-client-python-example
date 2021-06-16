# mender-client-python-example

Mender is an open source over-the-air (OTA) software updater for embedded Linux
devices. Mender comprises a client running at the embedded device, as well as a
server that manages deployments across many devices.

![Mender
logo](https://raw.githubusercontent.com/mendersoftware/mender/master/mender_logo.png)

This repository contains simple example applications in Python that communicate
with the Mender client on a device via D-Bus to demonstrate some of the use
cases.

The code in this repository is meant to educate and showcase the Mender D-Bus
API capabilities. Please keep in mind that for simplicity error handling and
failure recovery is not implemented in most cases, and we strongly discourage
the use of the code as-is in production applications.

## Documentation

### API documentation

The D-Bus APIs of the Mender client are documented in the [Device-side API
section of the Mender Docs](https://docs.mender.io/device-side-api).

### D-Bus documentation

A basic understanding of the D-Bus concepts are required in order to understand
the code in this repository. You can find an [introduction to D-Bus
here](https://www.freedesktop.org/wiki/IntroductionToDBus/).

### Python PyDBus package

The examples in this repository are using the PyDBus package, which provides a
modern and pythonic abstraction of the D-Bus API. You can browse its
[documentation here](https://pydbus.readthedocs.io/en/latest/index.html) and the
[source code here](https://github.com/LEW21/pydbus).

If you are new to D-Bus, you might find [this
article](https://pydbus.readthedocs.io/en/latest/dbusaddressing.html) from the
PyDBus documentation helpful.

## Install

### Requirements

The examples require Python 3 and it's package manager `pip`. We also use `git`
to get the source.

For Debian based distributions install the required dependencies with:

```
sudo apt-get install -y git python3 python3-pip
```

### Install

Clone this repository into the device running Mender

```
git clone https://github.com/mendersoftware/mender-client-python-example.git
```

Install the example applications:
```
sudo pip3 install mender-client-python-example/
```

You can now launch the different examples, for instance:
```
sudo mender-update-flow-control
```

## Contributing

We welcome and ask for your contribution. If you would like to contribute to
Mender, please read our guide on how to best get started [contributing code or
documentation](https://github.com/mendersoftware/mender/blob/master/CONTRIBUTING.md).

## License

Mender is licensed under the Apache License, Version 2.0. See
[LICENSE](https://github.com/mendersoftware/mender-client-python-example/blob/master/LICENSE)
for the full license text.

## Security disclosure

We take security very seriously. If you come across any issue regarding
security, please disclose the information by sending an email to
[security@mender.io](security@mender.io). Please do not create a new public
issue. We thank you in advance for your cooperation.

## Connect with us

* Join the [Mender Hub discussion forum](https://hub.mender.io)
* Follow us on [Twitter](https://twitter.com/mender_io). Please feel free to
  tweet us questions.
* Fork us on [Github](https://github.com/mendersoftware)
* Create an issue in the [bugtracker](https://tracker.mender.io/projects/MEN)
* Email us at [contact@mender.io](mailto:contact@mender.io)
* Connect to the [#mender IRC channel on Libera](https://web.libera.chat/?#mender)
