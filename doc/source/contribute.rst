Contribute
==========

Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to the FileTransfer Tool.

The following contribution information is specific to the FileTransfer Tool.

Install in development mode
---------------------------

Installing the FileTransfer Tool in development mode allows you
to modify the source and enhance it.

#.  Clone the repository and enter the newly created directory:

    .. code:: bash

        git clone https://github.com/ansys-internal/ansys-tools-filetransfer
        cd ansys-tools-filetransfer

#.  Install dependencies:

    .. code:: bash

        python -m pip install pipx
        pipx ensurepath
        pipx install poetry
        pipx install pip
        pipx install tox

    The project uses `Poetry`_ to manage the development environment.

#.  Create a virtual environment and install the package with the
    development dependencies:

    .. code:: bash

        poetry install --all-extras

#.  Activate the virtual environment:

    .. code:: bash

        poetry shell

Test
----

You can run the tests for the FileTransfer Tool with either
a local executable of the server or with a Docker container.

Unless you are contributing to development of the server, using a Docker
container is recommended.

#.  Pull the Docker image:

    .. code:: bash

        docker pull ghcr.io/ansys-internal/tools-filetransfer:latest

#.  Run the tests with `tox`_.

    For example, this command runs the test for Python 3.10:

    .. code:: bash

        tox -e py310

Alternatively, you can run the tests directly via `pytest_`. Ensure that the
development virtual environment is activated:

.. code:: bash

    poetry shell

Then, run the tests:

.. code:: bash

    pytest

Running the tests directly via ``pytest`` also allows you to pass additional
arguments. For example, this command runs the tests with a local executable of
the server:

.. code:: bash

    pytest --server-bin /path/to/server/executable

This command runs the tests with a different Docker image of the server:

.. code:: bash

    pytest --server-image <image_name>

Build documentation
-------------------

You can build the documentation with this ``tox`` command:

.. code:: bash

    tox -e doc

The resulting files are located in the ``doc/_build/html`` directory.


Run style checks
----------------

The style checks use `pre-commit`_ and can be run using this `tox`_ command:

.. code:: bash

    tox -e style

You can also configure the style checks to run automatically before each ``git commit``
with this command:

.. code:: bash

    pre-commit install


.. LINKS AND REFERENCES
.. _Poetry: https://python-poetry.org
.. _tox: https://tox.wiki/
.. _pytest: https://docs.pytest.org/en/stable/
.. _pre-commit: https://pre-commit.com/
