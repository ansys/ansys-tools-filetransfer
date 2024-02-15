Contribute
==========

Overall guidance on contributing to a PyAnsys library appears in
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_
in the *PyAnsys developer's guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to the Filetransfer Tool.

The following contribution information is specific to the Filetransfer Tool.

Install in development mode
---------------------------

Installing the Filetransfer Tool Python Client in development mode allows you
to modify the source and enhance it.


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
----

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
-------------------

The documentation can be built with ``tox``:

.. code:: bash

    tox -e doc

The resulting files will be in ``doc/_build/html``.

Run style checks
----------------

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
