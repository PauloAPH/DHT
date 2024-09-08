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
"""The Python implementation of the gRPC DHT server."""

from concurrent import futures

import grpc
import hashlib
import logging

from protos import dht_pb2
from protos import dht_pb2_grpc

class DHTServicer(dht_pb2_grpc.DHTServicer):
    """Provides methods that implement functionality of DHT server."""

    def __init__(self):
        print("Server runnig: Hello World!")

    def Register(self, request, context):

        return dht_pb2.Response()


    



class Server():     
    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        dht_pb2_grpc.add_DHTServicer_to_server(
            DHTServicer(), server
        )
        server.add_insecure_port("[::]:50051")
        server.start()
        server.wait_for_termination()


if __name__ == "__main__":
    # logging.basicConfig()
    # serve()
