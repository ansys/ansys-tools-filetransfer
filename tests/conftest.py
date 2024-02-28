# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from contextlib import closing, contextmanager, suppress
import os
import pathlib
import secrets
import socket
import subprocess
import sys
import tempfile
import time

import grpc
from grpc_health.v1.health_pb2 import HealthCheckRequest, HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import HealthStub
import pytest

SERVER_BIN_OPTION_KEY = "--server-bin"
DOCKER_IMAGENAME_OPTION_KEY = "--docker-image"

__all__ = ["pytest_addoption", "client_tmpdir", "server_channel"]


def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        SERVER_BIN_OPTION_KEY,
        action="store",
        help="Path of the server executable",
    )
    parser.addoption(
        DOCKER_IMAGENAME_OPTION_KEY,
        action="store",
        help=("Docker image to be used for running the test."),
        default="ghcr.io/ansys/tools-filetransfer:latest",
    )


@pytest.fixture
def client_tmpdir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture(scope="session")
def server_tmpdir(request, mounted_tmpdir):
    if request.config.getoption(SERVER_BIN_OPTION_KEY):
        yield mounted_tmpdir
    else:
        yield pathlib.PurePosixPath("/tmp")


@pytest.fixture(scope="session")
def mounted_tmpdir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture(scope="session")
def server_channel(request, server_tmpdir, mounted_tmpdir):
    server_bin = request.config.getoption(SERVER_BIN_OPTION_KEY)

    port = _find_free_port()
    if server_bin:
        launch_context = _launch_local(server_bin=server_bin, port=port)
    else:
        launch_context = _launch_docker(
            docker_imagename=request.config.getoption(DOCKER_IMAGENAME_OPTION_KEY),
            mounted_tmpdir=mounted_tmpdir,
            server_tmpdir=server_tmpdir,
            port=port,
        )

    with launch_context as proc:
        channel = grpc.insecure_channel(f"localhost:{port}")

        # check if the server has started by using the HealthCheck
        health_stub = HealthStub(channel)
        start_time = time.time()
        timeout = 30.0
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
            raise RuntimeError(f"Server failed to start.")

        yield channel


@contextmanager
def _launch_local(*, server_bin, port):
    cmd = [server_bin, f"--server-address=0.0.0.0:{port}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    yield proc
    proc.kill()


@contextmanager
def _launch_docker(*, docker_imagename, port, mounted_tmpdir, server_tmpdir):
    docker_containername = f"filetransfer_test_{secrets.token_urlsafe(8)}"

    cmd = [
        "docker",
        "run",
        "-v",
        f"/{pathlib.Path(mounted_tmpdir).resolve().as_posix().replace(':', '')}:{server_tmpdir}",
    ]
    if sys.platform == "linux":
        cmd += ["-u", f"{os.getuid()}:{os.getgid()}"]
    cmd += [
        "-p",
        f"{port}:50000/tcp",
        "--name",
        docker_containername,
        docker_imagename,
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    yield proc
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
