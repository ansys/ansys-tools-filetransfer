.. toctree::
   :hidden:
   :maxdepth: 3

   usage
   api/index
   contribute

Ansys FileTransfer Tool documentation
=====================================

The Ansys FileTransfer Tool is a simple gRPC API for moving files between
a client and a remote server. Its target use case are local Docker deployments or
simple remote deployments.

This documentation describes the FileTransfer Tool itself. For information on the
server component, see the
`FileTransfer Tool Server documentation <https://filetransfer.tools.docs.pyansys.com/version/dev/index.html>`_.

.. warning::

   The FileTransfer Tool does not provide any security measures. Any file
   on the server component can be accessed by any client. Without additional security
   measures, it is unsuited for use over an untrusted network.

.. grid:: 1 1 2 2
    :gutter: 2

    .. grid-item-card:: Getting started :fa:`person-running`
        :link: usage
        :link-type: doc

        Explains how to install the FileTransfer Tool in user mode and then how
        to use it from a Python script.

    .. grid-item-card:: API reference :fa:`book-bookmark`
        :link: api/index
        :link-type: doc

        Describes FileTransfer Tool API endpoints so that you can understand how to interact with
        them programmatically.

    .. grid-item-card:: Contribute :fa:`people-group`
        :link: contribute
        :link-type: doc

        Provides information on how to install the FileTransfer Tool in developer mode and make contributions
        to the codebase and documentation.
