Getting started
---------------

Installation
^^^^^^^^^^^^

Install the latest version of the package from PyPI:

.. code-block:: bash

    pip install ansys-tools-filetransfer

You should use a `virtual environment <https://docs.python.org/3/library/venv.html>`_,
because it keeps Python packages isolated from your system Python.

Usage
^^^^^

To get started, import the package:

.. code-block:: python

    import ansys.tools.filetransfer as ft

The package contains a single class, :class:`.Client`, which is used to
communicate with the server. The class can be instantiated with the server
address and port number:

.. code-block:: python

    client = ft.Client.from_server_address("localhost:50052")

Alternatively, the class can be instantiated with a :class:`grpc.Channel`:

.. code-block:: python

    import grpc
    channel = grpc.insecure_channel("localhost:50052")
    client = ft.Client(channel)

This allows you to change how the channel is created.

The client can be used to upload and download files:

.. code-block:: python

    client.upload_file(local_filename="file_local.txt", remote_filename="file_remote.txt")
    client.download_file(remote_filename="file_remote.txt", local_filename="file_local_copy.txt")
