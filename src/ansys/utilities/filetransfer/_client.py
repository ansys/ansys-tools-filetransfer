# -*- coding: utf-8 -*-
#
# Copyright 2022 ANSYS, Inc. Unauthorized use, distribution, or duplication is prohibited.
#
"""A high-level Python Client for the Ansys Filetransfer utility.

This module implements a high-level Python client for interacting with
the Ansys filetransfer utility via gRPC.
"""
import hashlib
import os
import stat
from typing import Generator, Optional

import grpc

from ansys.api.utilities.filetransfer.v1 import (
    file_transfer_service_pb2,
    file_transfer_service_pb2_grpc,
)

from ._log import LOGGER


class Client:
    """Ansys Filetransfer Utility high-level client module.

    The filetransfer client provides a high-level API for uploading and
    downloading files to the filetransfer server.
    """

    def __init__(self, channel: grpc.Channel, max_message_length: Optional[int] = None):
        """Initialize the client.

        Parameters
        ----------
        channel :
            The gRPC channel on which the client communicates with the
            server.
        max_message_length :
            The maximum message size which is configured on the given
            channel. Note that this does **not** change the channel
            configuration. The parameter is used to check that the
            ``chunk_size`` used for up- and download fits within the
            ``max_message_length``, with some slack.
        """
        self._channel = channel
        if max_message_length is None:
            # Set the max_message_length to 4GB if it is not set.
            # This is the technical limit, see
            # https://groups.google.com/g/google-cloud-endpoints/c/sYT4BopjohI
            self._max_message_length = 1 << 32
        else:
            self._max_message_length = max_message_length
        self._filetransfer_stub = file_transfer_service_pb2_grpc.FileTransferServiceStub(
            self._channel
        )

    @classmethod
    def from_server_address(
        cls,
        server_address: str,
        *,
        max_message_length: int = 1 << 17,
    ) -> "Client":
        """Initialize the client from a server URL.

        Parameters
        ----------
        server_address :
            The IPv4/IPv6 address and port of the server to connect to, e.g. `10.0.0.42:12345`
        max_message_length :
            Maximum length of messages sent over the channel, in bytes.

        Returns
        -------
        :
            The instantiated Filetransfer Client.
        """
        if not server_address:
            raise ValueError("Empty server address given.")

        channel = grpc.insecure_channel(
            server_address,
            options=[
                ("grpc.max_send_message_length", max_message_length),
                ("grpc.max_receive_message_length", max_message_length),
            ],
        )
        return cls(channel=channel, max_message_length=max_message_length)

    # def _check_result(
    #     self, result: file_transfer_service_pb2.Result, last_error_msg: Optional[str] = None
    # ) -> None:
    #     """Check the result and raise an exception if not OK."""
    #     if not result.ok:
    #         raise RuntimeError(
    #             result.message + (("\n%s" % last_error_msg) if last_error_msg is not None else ""),
    #             result.status_code,
    #         )

    def _log_progress(
        self, call: str, progress: file_transfer_service_pb2.ProgressResponse
    ) -> None:
        # if progress.message:
        #     LOGGER.debug(
        #         "[%s] progress : %d %% (%s)" % (call, progress.state, str(progress.message))
        #     )
        # else:
        LOGGER.debug("[%s] progress : %d %%" % (call, progress.state))

    def _check_chunk_size(self, chunk_size: int) -> None:
        if chunk_size > self._max_message_length:
            raise ValueError(
                f"The chunk size '{chunk_size}' exceeds the maximum message length "
                f"'{self._max_message_length}' of the gRPC channel."
            )
        elif (2 * chunk_size) > self._max_message_length:
            LOGGER.warning(
                f"The chunk size '{chunk_size}' is close to the maximum message length "
                f"'{self._max_message_length}' of the gRPC channel."
            )

    def download_file(
        self,
        remote_filename: str,
        local_filename: str,
        chunk_size: int = 1 << 16,
        compute_sha1_checksum: bool = True,
    ) -> None:
        """Download a file from the server.

        Parameters
        ----------
        remote_filename :
            The name of the remote file to be downloaded.
        local_filename :
            The name of the local file to be created.
        chunk_size :
            The max. size of a chunk of data to be transferred per request (default 64K).
        compute_sha1_checksum :
            Flag whether to compute the SHA1-checksum of the file to be downloaded on the
            server-side or not (default True).

        Raises
        ------
        RuntimeError :
            Raises a RuntimeError in case of a response indicating an error on the server-side.
        ValueError :
            Raises a ValueError in case the checksums between the downloaded and remote
            file do not match.

        """
        self._check_chunk_size(chunk_size)

        sha1sum = "0"
        n_bytes_received = 0

        # download iterator
        def download_file_iterator() -> Generator[
            file_transfer_service_pb2.DownloadFileRequest, None, None
        ]:
            # 1) send info
            yield file_transfer_service_pb2.DownloadFileRequest(
                initialize=file_transfer_service_pb2.DownloadFileRequest.Initialize(
                    filename=remote_filename,
                    chunk_size=chunk_size,
                    compute_sha1_checksum=compute_sha1_checksum,
                )
            )
            # 2) receive data
            yield file_transfer_service_pb2.DownloadFileRequest(
                receive_data=file_transfer_service_pb2.DownloadFileRequest.ReceiveData()
            )
            # 3) finalize
            yield file_transfer_service_pb2.DownloadFileRequest(
                finalize=file_transfer_service_pb2.DownloadFileRequest.Finalize()
            )

        # stream data
        with open(local_filename, "wb") as f:
            for response in self._filetransfer_stub.DownloadFile(download_file_iterator()):
                # self._check_result(response.result)
                self._log_progress("download_file", response.progress)
                if response.WhichOneof("sub_step") == "file_info":
                    # file_size = int(response.file_info.size)
                    sha1sum = str(response.file_info.sha1.hex_digest)
                elif response.WhichOneof("sub_step") == "file_data":
                    f.write(response.file_data.data)
                    n_bytes_received += len(response.file_data.data)
                else:
                    pass

        # size_of_file_in_bytes = os.stat(local_filename)[stat.ST_SIZE]
        if compute_sha1_checksum:
            hexdigest = _get_file_hash(local_filename, "sha1")
            if hexdigest != sha1sum:
                raise ValueError(
                    "Checksum mismatch (%s != %s) between local and remote file, download failed!"
                    % (hexdigest, sha1sum)
                )

    def upload_file(
        self, local_filename: str, remote_filename: str, chunk_size: int = 1 << 16
    ) -> None:
        """Upload a file to the server.

        Parameters
        ----------
        local_filename : :obj:`string`
            The name of the local file to be uploaded.
        remote_filename : :obj:`string`
            The name of the remote file to be created.
        chunk_size : :obj:`int`
            The max. size of a chunk of data to be transferred per request (default 64K).

        Raises
        ------
        RuntimeError :
            Raises a RuntimeError in case of a response indicating an error on the server-side.

        """
        self._check_chunk_size(chunk_size)

        # prepare
        size_of_file_in_bytes = os.stat(local_filename)[stat.ST_SIZE]
        sha1sum = _get_file_hash(local_filename, "sha1")

        # upload iterator
        def upload_file_iterator() -> Generator[
            file_transfer_service_pb2.UploadFileRequest, None, None
        ]:
            # 1) send info
            yield file_transfer_service_pb2.UploadFileRequest(
                initialize=file_transfer_service_pb2.UploadFileRequest.Initialize(
                    file_info=file_transfer_service_pb2.FileInfo(
                        name=remote_filename,
                        size=size_of_file_in_bytes,
                        sha1=file_transfer_service_pb2.SHA1(hex_digest=sha1sum),
                    )
                )
            )
            # 2) stream file content in chunks
            with open(local_filename, "rb") as f:
                offset = 0
                for chunk in iter(lambda: f.read(chunk_size), ""):
                    # send data
                    yield file_transfer_service_pb2.UploadFileRequest(
                        send_data=file_transfer_service_pb2.UploadFileRequest.SendData(
                            file_data=file_transfer_service_pb2.FileChunk(offset=offset, data=chunk)
                        )
                    )
                    if len(chunk) == 0:
                        break
                    offset += len(chunk)
            # 3) finalize
            yield file_transfer_service_pb2.UploadFileRequest(
                finalize=file_transfer_service_pb2.UploadFileRequest.Finalize()
            )

        # stream data
        for response in self._filetransfer_stub.UploadFile(upload_file_iterator()):
            # self._check_result(response.result)
            self._log_progress("upload_file", response.progress)


def _get_file_hash(filename: str, algorithm: str = "md5") -> str:
    """Get the hash checksum of a file.

    Parameters
    ----------
    filename : :obj:`string`
        The name of the file to be processed.
    algorithm : :obj:`string`, optional
        The hash algorithm to be used (default md5).

    Returns
    -------
    obj:`list`
        The hash of the file.
    """
    method = hashlib.new(algorithm)
    with open(filename, "rb") as f:
        chunkSize = 128 * method.block_size
        for chunk in iter(lambda: f.read(chunkSize), ""):
            if len(chunk) == 0:
                break
            method.update(chunk)
    return method.hexdigest()
