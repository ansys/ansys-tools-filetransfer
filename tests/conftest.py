# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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
import uuid

import grpc
from grpc_health.v1.health_pb2 import HealthCheckRequest, HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import HealthStub
import pytest

from ansys.tools.filetransfer import InsecureOptions, MTLSOptions, UDSOptions

TEST_ROOT_DIR = pathlib.Path(__file__).parent.resolve()

SERVER_BIN_OPTION_KEY = "--server-bin"
DOCKER_IMAGENAME_OPTION_KEY = "--docker-image"
TRANSPORT_MODE_OPTION_KEY = "--transport-mode"

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
        default="ghcr.io/ansys-internal/tools-filetransfer:latest",
    )
    parser.addoption(
        TRANSPORT_MODE_OPTION_KEY,
        action="store",
        help="Transport mode to be used for the tests. The docker test option does not support 'uds' mode.",
        default=None,
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
    transport_mode = request.config.getoption(TRANSPORT_MODE_OPTION_KEY)
    use_docker_launch = server_bin is None

    if use_docker_launch and transport_mode == "uds":
        raise RuntimeError("Docker launch tests do not support UDS transport mode.")
    if transport_mode not in ("uds", "mtls", "insecure", None):
        raise ValueError(f"Unsupported transport mode: {transport_mode}")

    if transport_mode is None:
        transport_mode = "mtls" if use_docker_launch else "uds"

    if transport_mode == "uds":
        assert not use_docker_launch
        uds_id = uuid.uuid4().hex
        transport_options = UDSOptions(
            uds_id=uds_id,
        )
        launch_context = _launch_local_uds(server_bin=server_bin, uds_id=uds_id)
    elif transport_mode == "mtls":
        port = _find_free_port()
        certs_dir = TEST_ROOT_DIR / "insecure_certs"
        transport_options = MTLSOptions(
            port=port,
            certs_dir=certs_dir,
        )
        if use_docker_launch:
            launch_context = _launch_docker(
                transport_mode=transport_mode,
                docker_imagename=request.config.getoption(DOCKER_IMAGENAME_OPTION_KEY),
                mounted_tmpdir=mounted_tmpdir,
                server_tmpdir=server_tmpdir,
                port=port,
            )
        else:
            launch_context = _launch_local_mtls(
                server_bin=server_bin,
                port=port,
                certs_dir=certs_dir,
            )
    elif transport_mode == "insecure":
        port = _find_free_port()
        transport_options = InsecureOptions(port=port)
        if use_docker_launch:
            launch_context = _launch_docker(
                transport_mode=transport_mode,
                docker_imagename=request.config.getoption(DOCKER_IMAGENAME_OPTION_KEY),
                mounted_tmpdir=mounted_tmpdir,
                server_tmpdir=server_tmpdir,
                port=port,
            )
        else:
            launch_context = _launch_local_insecure(
                server_bin=server_bin,
                port=port,
            )
    else:
        raise ValueError(f"Unsupported transport mode: {transport_mode}")

    with launch_context:
        channel = transport_options.create_channel()

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
def _launch_local_uds(*, server_bin, uds_id):
    cmd = [server_bin, "--transport-mode=uds", f"--uds-id={uds_id}"]
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True
        )
        yield proc
    finally:
        proc.kill()


@contextmanager
def _launch_local_mtls(*, server_bin, port, certs_dir):
    cmd = [
        server_bin,
        "--transport-mode=mtls",
        f"--port={port}",
        f"--certs-dir={certs_dir}",
    ]
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True
        )
        yield proc
    finally:
        proc.kill()


@contextmanager
def _launch_local_insecure(*, server_bin, port):
    cmd = [server_bin, "--transport-mode=insecure", f"--port={port}"]
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True
        )
        yield proc
    finally:
        proc.kill()


@contextmanager
def _launch_docker(*, transport_mode, docker_imagename, port, mounted_tmpdir, server_tmpdir):
    docker_containername = f"filetransfer_test_{secrets.token_urlsafe(8)}"

    if transport_mode == "mtls":
        extra_docker_opts = [
            "-v",
            f"{TEST_ROOT_DIR / 'insecure_certs'}:/certs:ro",
        ]
        extra_server_opts = [
            "--transport-mode=mtls",
            "--certs-dir=/certs",
        ]
    else:
        assert transport_mode == "insecure"
        extra_docker_opts = []
        extra_server_opts = ["--transport-mode=insecure"]

    cmd = [
        "docker",
        "run",
        "--detach",
        "-v",
        f"/{pathlib.Path(mounted_tmpdir).resolve().as_posix().replace(':', '')}:{server_tmpdir}",
    ] + extra_docker_opts
    if sys.platform == "linux":
        cmd += ["-u", f"{os.getuid()}:{os.getgid()}"]
    cmd += [
        "-p",
        f"127.0.0.1:{port}:50000",  # limits the binding to localhost
        "--name",
        docker_containername,
        docker_imagename,
        "--port=50000",
        "--host=0.0.0.0",
        "--allow-remote-host",
    ] + extra_server_opts
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Wait for the server to start. For some reason, the health check fails without this.
        # Maybe a race condition on the port binding?
        time.sleep(1.0)
        yield
    finally:
        subprocess.check_call(["docker", "container", "stop", "-t", "0", docker_containername])
        subprocess.check_call(["docker", "container", "rm", docker_containername])


def _find_free_port() -> int:
    """Find a free port on localhost.

    .. note::

        There is no guarantee that the port is *still* free when it is
        used by the calling code.
    """
    with closing(socket.socket()) as sock:
        sock.bind(("", 0))  # bind to a free port
        return sock.getsockname()[1]  # type: ignore
