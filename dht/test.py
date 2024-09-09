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
import logging

from protos import dht_pb2
from protos import dht_pb2_grpc

class DHTServicer(dht_pb2_grpc.DHTServicer):
    """Provides methods that implement functionality of DHT server."""

    def __init__(self, port, id, p_node, n_node):
        print("Server runnig: Hello World!")
        self.port = port
        self.id = id
        self.p_node = p_node
        self.n_node = n_node
        

    def Hello(self, request, context):
        print("respondendo node " + request.port)
        return dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
    
    def Try_Join(self, request, context):
        print("No " + request.port + " tentando entrar na rede")
        if request.id > self.p_node and request.id < self.id:
            return dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
        else:
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_dht(self.n_node_ip, self.n_node_port)

class Client():
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
        

    def send_hello(self, ip, port):
        print(port)
        with grpc.insecure_channel("localhost:" + port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            node = dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
            response = stub.Hello(node)
            print(response.port)


    def join_dht(self, ip, port):
        with grpc.insecure_channel("localhost:" + port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            join_req = dht_pb2.Join(ip = self.ip, port = self.port, id = int(self.id))
            resp = stub.Try_join(join_req)





class Server():   
    def __init__(self):
        self.ip = input("Entre com IP ")
        self.port = input("Entre com a porta ")
        self.node = input("Entre com o ID do node ")
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        dht_pb2_grpc.add_DHTServicer_to_server(
            DHTServicer(self.port, self.node, "a", "a"), self.grpc_server
        )
        self.grpc_server.add_insecure_port("[::]:" + self.port)
        
    def start(self):
        self.grpc_server.start()


if __name__ == "__main__":
    print("Hello World!")
    # logging.basicConfig()
    server_dht = Server()
    server_dht.start()
    client_dht = Client(server_dht.ip, server_dht.port, server_dht.node)
    client_dht.join_dht("localhost:", "50000")
