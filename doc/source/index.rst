.. toctree::
   :hidden:
   :maxdepth: 3

   self
   usage
   api/index
   contribute

Filetransfer Tool Python Client
-------------------------------

The Ansys filetransfer tool provides a simple gRPC API for moving files between
a client and a server. Its target use case are local Docker deployments, or
simple remote deployments.

The tool is composed of two parts:

- A Python client (the component described here).
- A C++ server, see the `ansys-tools-filetransfer-server repository <https://github.com/ansys-internal/ansys-tools-filetransfer-server>`_.

.. warning::

   The filetransfer tool does not provide any security measures. Any file
   on the server component can be accessed by any client. Without additional security
   measures, it is unsuited for use over an untrusted network.

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: :octicon:`rocket` Installation and usage
        :link: usage
        :link-type: doc

        Contains installation instructions and usage instructions.

    .. grid-item-card:: :octicon:`file-code` API reference
        :link: api/index
        :link-type: doc

        Describes the public Python classes, methods, and functions.

    .. grid-item-card:: :octicon:`code` Contribute
        :link: contribute
        :link-type: doc

        Provides developer installation and usage information.
