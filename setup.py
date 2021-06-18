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
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mender-python-client-example",
    version="0.0.1",
    license="Apache 2.0",
    author="Mendersoftware",
    author_email="contact@mender.io",
    description="A Python example application to use Mender client D-Bus interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mendersoftware/mender-python-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Development Status :: 2 - Pre-Alpha",
    ],
    keywords=["mender", "OTA", "updater", "dbus"],
    packages=["mender_examples.update_flow_control"],
    install_requires=["pydbus"],
    entry_points={"console_scripts": ["mender-update-flow-control=mender_examples.update_flow_control.update_flow_control:main"]},
    package_dir={"mender_examples": "examples"},
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
)
