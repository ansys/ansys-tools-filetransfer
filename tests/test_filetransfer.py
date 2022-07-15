import os
import secrets

import pytest

from ansys.utilities.filetransfer import Client


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
