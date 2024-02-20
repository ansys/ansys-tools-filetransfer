Getting started
===============

Installation
------------

Install the latest version of the FileTransfer Tool from PyPI with this command:

.. code-block:: bash

    pip install ansys-tools-filetransfer

You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_
because it keeps Python packages isolated from your system Python.

Usage
-----

To begin using the FileTransfer Tool, import the package with this command:

.. code-block:: python

    import ansys.tools.filetransfer as ft

The FileTransfer Tool API contains a single class, :class:`.Client`, which is used to
communicate with the server. You instantiate this class with the server
address and port number:

.. code-block:: python

    client = ft.Client.from_server_address("localhost:50052")

Alternatively, you can instantiate the :class:`.Client` with the :class:`grpc.Channel` class:

.. code-block:: python

    import grpc
    channel = grpc.insecure_channel("localhost:50052")
    client = ft.Client(channel)

The preceding code allows you to change how the channel is created.

Following instantiation, you can use the client to upload and download files:

.. code-block:: python

    client.upload_file(local_filename="file_local.txt", remote_filename="file_remote.txt")
    client.download_file(remote_filename="file_remote.txt", local_filename="file_local_copy.txt")
