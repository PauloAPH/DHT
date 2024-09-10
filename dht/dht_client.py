# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the gRPC route guide client."""

from __future__ import print_function

from datetime import datetime, timezone
import grpc
import logging

from protos import dht_pb2
from protos import dht_pb2_grpc

class Client():
    def init():
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
        Client.send_hello(stub)

    def send_hello(stub):
        node = dht_pb2.Node(adress = "1")
        response = stub.hello(node)
        print(response.adress)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    Client.init()

if __name__ == "__main__":
    logging.basicConfig()
    run()
