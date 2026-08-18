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

The FileTransfer Tool API contains a :class:`.Client` class, which is used to
communicate with the server. You instantiate this class with the transport options
used to connect to the server.

.. code-block:: python

    client = ft.Client.from_transport_options(
        transport_options=ft.UDSOptions()
    )

The ``transport_options`` parameter allows you to specify how the client connects
to the server. To connect with mutual TLS (mTLS), provide an
:class:`.MTLSOptions` instance:

.. code-block:: python

    client = ft.Client.from_transport_options(
        transport_options=ft.MTLSOptions(
            host="localhost",
            port=50000,
            certs_dir="path/to/certificates/directory"
        )
    )

Alternatively, you can instantiate the :class:`.Client` class directly with a pre-existing
gRPC channel:

.. code-block:: python

    import grpc

    channel = <create your gRPC channel here>
    client = ft.Client(channel=channel)

Following instantiation, you can use the client to upload and download files:

.. code-block:: python

    client.upload_file(local_filename="file_local.txt", remote_filename="file_remote.txt")
    client.download_file(remote_filename="file_remote.txt", local_filename="file_local_copy.txt")
