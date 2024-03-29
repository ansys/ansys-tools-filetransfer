FileTransfer Tool
=================

|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/ansys-tools-filetransfer?logo=pypi
   :target: https://pypi.org/project/ansys-tools-filetransfer/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-tools-filetransfer.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-tools-filetransfer
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys/ansys-tools-filetransfer/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys/ansys-tools-filetransfer
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys/ansys-tools-filetransfer/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/ansys-tools-filetransfer/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


The Ansys FileTransfer Tool provides a simple gRPC API for moving files between
a client and a server. Its target use case are local Docker deployments or
simple remote deployments.

The Ansys FileTransfer Tool is composed of two parts:

- A Python client, which is contained in this repository.
- A C++ server, which is contained in the
  `ansys-tools-filetransfer-server <https://github.com/ansys/ansys-tools-filetransfer-server>`_
  repository.

**WARNING**:

The FileTransfer Tool does not provide any security measures. Any file
on the server component can be accessed by any client. Without additional security
measures, it is unsuited for use over an untrusted network.


Documentation and issues
-------------------------

Documentation for the latest stable release of the FileTransfer Tool is hosted at
`FileTransfer Tool documentation <https://filetransfer.tools.docs.pyansys.com>`_.

The FileTransfer Tool documentation contains these sections:

- `Getting started <https://filetransfer.tools.docs.pyansys.com/version/dev/usage.html>`_:
  Explains how to install the FileTransfer Tool in user mode and then how
  to use it from a Python script.
- `API reference <https://filetransfer.tools.docs.pyansys.com/version/dev/api/index.html>`_:
  Describes FileTransfer Tool API endpoints so that you can understand how to interact with
  them programmatically.
- `Contribute <https://filetransfer.tools.docs.pyansys.com/version/dev/contribute.html>`_:
  Provides information on how to install the FileTransfer Tool in developer mode and make contributions
  to the codebase and documentation.

On the `FileTransfer Tool Issues <https://github.com/ansys/ansys-tools-filetransfer/issues>`_
page, you can create issues to report bugs and request new features. On the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.
