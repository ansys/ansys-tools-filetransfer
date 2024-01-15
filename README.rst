*******************************
Filetransfer Tool Python Client
*******************************

|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.9-blue
   :target: https://pypi.org/project/ansys-tools-filetransfer/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-tools-filetransfer.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-tools-filetransfer
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/ansys-internal/ansys-tools-filetransfer/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/ansys-internal/ansys-tools-filetransfer
   :alt: Codecov

.. |GH-CI| image:: https://github.com/ansys-internal/ansys-tools-filetransfer/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/ansys-internal/ansys-tools-filetransfer/actions/workflows/ci.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


The Ansys filetransfer tool provides a simple gRPC API for moving files between
a client and a server. Its target use case are local Docker deployments, or
simple remote deployments.

The tool is composed of two parts:
- A Python client, which is contained in this repository.
- A C++ server, which is contained in the `ansys-tools-filetransfer-server` repository.

.. warning::
    The filetransfer tool does not provide any security measures. Any file
    on the server component can be accessed by any client. Without additional security
    measures, it is unsuited for use over an untrusted network.

For usage instructions, please refer to the `documentation`_.

.. START_MARKER_FOR_SPHINX_DOCS

----------
Contribute
----------

Install in development mode
===========================

Installing the Filetransfer Tool Python Client in development mode allows you
to modify the source and enhance it.

Before contributing to the project, ensure that you are thoroughly familiar with
the `PyAnsys Developer's guide`_.

#.  Clone the repository and enter the newly created directory:

    .. code:: bash

        git clone https://github.com/ansys-internal/ansys-tools-filetransfer
        cd ansys-tools-filetransfer

#.  Install dependencies

    .. code:: bash

        python -m pip install pipx
        pipx ensurepath
        pipx install poetry
        pipx install pip
        pipx install tox

    The project uses `Poetry <https://python-poetry.org>`_
    to manage the development environment.

#.  Create a virtual environment and install the package with the
    development dependencies:

    .. code:: bash

        poetry install --all-extras


#.  Activate the virtual environment:

    .. code:: bash

        poetry shell

Test
====

The tests for the Filetransfer Tool Python Client can be run either with
a local executable of the server, or with a Docker container.

Unless you are developing the server, it is recommended to use the Docker
container.

#.  Pull the Docker image:

    .. code:: bash

        docker pull ghcr.io/ansys-internal/tools-filetransfer:latest

#.  Run the tests with ``tox`` (for example, for Python 3.10):

    .. code:: bash

        tox -e py310

Alternatively, you can run the tests directly via ``pytest``. Ensure that the
development virtual environment is activated:

.. code:: bash

    poetry shell

Then, run the tests:

.. code:: bash

    pytest

Running the tests directly via ``pytest`` also allows you to pass additional
arguments. For example, to run the tests with a local executable of the server:

.. code:: bash

    pytest --server-bin /path/to/server/executable

Or, to run the tests with a different server Docker image:

.. code:: bash

    pytest --server-image <image_name>


Build documentation
===================

The documentation can be built with ``tox``:

.. code:: bash

    tox -e doc

The resulting files will be in ``doc/_build/html``.

Run style checks
================

The style checks use `pre-commit`_ and can be run through `tox`_:

.. code:: bash

    tox -e style


The style checks can also be configured to run automatically before each ``git commit``:

.. code:: bash

    pre-commit install


.. LINKS AND REFERENCES
.. _documentation: https://filetransfer.tools.docs.pyansys.com
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pre-commit: https://pre-commit.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
