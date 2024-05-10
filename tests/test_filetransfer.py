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

import os
import secrets

import pytest

from ansys.tools.filetransfer import Client


def get_sizes():
    file_sizes = [0, 1, 100, 1 << 11, (1 << 11) + 1]
    chunk_sizes = [1, 5, 1 << 4, 1 << 10, 1 << 20]
    cases = []
    for f_size in file_sizes:
        for c_size in chunk_sizes:
            if (f_size / c_size) < 100:
                cases.append((f_size, c_size))
    return cases


@pytest.fixture(params=[True, False])
def compute_sha1_sum(request):
    return request.param


@pytest.mark.parametrize("size_cases", get_sizes())
def test_upload(server_channel, server_tmpdir, mounted_tmpdir, client_tmpdir, size_cases):
    file_size, chunk_size = size_cases
    filename = f"test_file_üñıçよð€_{secrets.token_hex(8)}"
    local_filename_in = str(client_tmpdir / filename)
    remote_filename = str(server_tmpdir / filename)
    local_filename_out = str(mounted_tmpdir / filename)

    content = os.urandom(file_size)
    with open(local_filename_in, mode="wb") as out_f:
        out_f.write(content)

    client = Client(server_channel)
    client.upload_file(local_filename_in, remote_filename, chunk_size=chunk_size)

    assert filename in [path.name for path in mounted_tmpdir.iterdir()]
    with open(local_filename_out, mode="rb") as in_f:
        content_out = in_f.read()

    assert content == content_out


@pytest.mark.parametrize("size_cases", get_sizes())
def test_download(
    server_channel, server_tmpdir, mounted_tmpdir, client_tmpdir, size_cases, compute_sha1_sum
):
    file_size, chunk_size = size_cases
    filename = f"test_file_üñıçよð€_{secrets.token_hex(8)}"

    local_filename_in = str(mounted_tmpdir / filename)
    remote_filename = str(server_tmpdir / filename)
    local_filename_out = str(client_tmpdir / filename)

    content = os.urandom(file_size)
    with open(local_filename_in, mode="wb") as out_f:
        out_f.write(content)

    client = Client(server_channel)
    client.download_file(
        remote_filename,
        local_filename_out,
        compute_sha1_checksum=compute_sha1_sum,
        chunk_size=chunk_size,
    )

    assert filename in [path.name for path in client_tmpdir.iterdir()]
    with open(local_filename_out, mode="rb") as in_f:
        content_out = in_f.read()

    assert content_out == content


def test_delete_inexistent(server_channel, server_tmpdir):
    client = Client(server_channel)
    with pytest.raises(OSError):
        client.delete_file(str(server_tmpdir / "inexistent_file"))
