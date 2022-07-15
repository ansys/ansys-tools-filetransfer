from contextlib import closing, suppress
import pathlib
import secrets
import socket
import subprocess
import tempfile
import time

import grpc
from grpc_health.v1.health_pb2 import HealthCheckRequest, HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import HealthStub
import pytest

DOCKER_IMAGENAME_OPTION_KEY = "--docker-image"

__all__ = ["pytest_addoption", "client_tmpdir", "server_channel"]


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        DOCKER_IMAGENAME_OPTION_KEY,
        action="store",
        help=("Docker image to be used for running the test."),
        default="ghcr.io/ansys/ansys-utilities-filetransfer-server:latest",
    )


@pytest.fixture
def client_tmpdir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture(scope="session")
def server_tmpdir():
    return pathlib.PurePosixPath("/tmp")


@pytest.fixture(scope="session")
def mounted_tmpdir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture(scope="session")
def server_channel(request, server_tmpdir, mounted_tmpdir):
    docker_containername = f"filetransfer_test_{secrets.token_urlsafe(8)}"
    port = _find_free_port()
    cmd = [
        "docker",
        "run",
        "-v",
        f"/{pathlib.Path(mounted_tmpdir).resolve().as_posix().replace(':', '')}:{server_tmpdir}",
        "-p",
        f"{port}:50000/tcp",
        "--name",
        docker_containername,
        request.config.getoption(DOCKER_IMAGENAME_OPTION_KEY),
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    channel = grpc.insecure_channel(f"localhost:{port}")

    # check if the server has started by using the HealthCheck
    health_stub = HealthStub(channel)
    start_time = time.time()
    timeout = 10.0
    while time.time() - start_time <= timeout:
        with suppress(grpc.RpcError):
            res = health_stub.Check(
                request=HealthCheckRequest(),
                timeout=timeout / 3,
            )
            if res.status == HealthCheckResponse.ServingStatus.SERVING:
                break
        time.sleep(timeout / 100)
    else:
        raise RuntimeError(f"Docker container failed to start:\n{proc.stderr.read()}")

    yield channel
    subprocess.check_call(["docker", "container", "stop", "-t", "0", docker_containername])


def _find_free_port() -> int:
    """Find a free port on localhost.

    .. note::

        There is no guarantee that the port is *still* free when it is
        used by the calling code.
    """
    with closing(socket.socket()) as sock:
        sock.bind(("", 0))  # bind to a free port
        return sock.getsockname()[1]  # type: ignore
