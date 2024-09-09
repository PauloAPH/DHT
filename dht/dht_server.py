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

from google.protobuf import empty_pb2


from protos import dht_pb2
from protos import dht_pb2_grpc

class DHTServicer(dht_pb2_grpc.DHTServicer):
    """Provides methods that implement functionality of DHT server."""

    def __init__(self, port, id):
        print("Server runnig: Hello World!")
        self.port = port
        self.id = id
        self.n_node_id =  ""
        self.n_node_adr =  ""
        self.p_node_id = "" 
        self.p_node_adr =  ""

    def print_all(self):
        print(self.n_node_id)
        print(self.n_node_adr)
        print(self.p_node_id)
        print(self.p_node_adr)
        

    def Hello(self, request, context):
        print("respondendo node " + request.port)
        return dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
    
    def Try_Join(self, request, context):
        print("No " + request.port + " tentando entrar na rede")
        if self.p_node_id == "" or (int(request.id) > int(self.p_node_id) and int(request.id) < int(self.id)):
            print("Enviando resposta")
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.port, self.p_node_id, self.p_node_adr)

        else:
            print("Encaminhando req")
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_dht(self.n_node_ip, self.n_node_port)
        return empty_pb2.Empty()
    
    def Join_ok(self, request, context):
        print("Resposta de entrada na rede recebida")
        self.n_node_id  = request.next_id 
        self.n_node_adr = request.next_adress 
        self.p_node_id  = request.pre_id 
        self.p_node_adr = request.pre_adress 
        self.print_all()
        return empty_pb2.Empty()


class Client():
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
        

    def send_hello(self):
        with open("dhtList.txt", "r") as file:
            ports = file.readlines()
            ports = [name.strip() for name in ports]  
            ok = 0
            for port in ports:
                with grpc.insecure_channel(port) as channel:
                    stub = dht_pb2_grpc.DHTStub(channel)
                    node = dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
                    try:
                        response = stub.Hello(node)
                        if response.port:
                            print(f"Greeter client received: {response.port}")
                            port_ok = port
                            ok = 1
                            break
                    except grpc.RpcError as rpc_error:
                        print(f"Tentando o prox host")
            if ok == 0:
                print("nenhum nó encontrado, iniciando dht")
                return ""
            else:
                print("no encontrado" + port_ok)
                return port_ok

    def join_dht(self, adress):
        with grpc.insecure_channel(adress) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            node = dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
            stub.Try_Join(node)


    def join_response(self, n_id, n_port, p_node_id, p_node_adr):
        print(self.ip + self.port)
        with grpc.insecure_channel(self.ip + self.port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            join_data = dht_pb2.JoinOk(next_id = n_id, next_adress = n_port, pre_id = p_node_id, pre_adress = p_node_adr)
            stub.Join_ok(join_data)




class Server():   
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id

        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        dht_pb2_grpc.add_DHTServicer_to_server(
            DHTServicer(self.port, self.id), self.grpc_server
        )
        self.grpc_server.add_insecure_port("[::]:" + self.port)


    def start(self):
        self.grpc_server.start()

    def wait(self):
        self.grpc_server.wait_for_termination()
        


if __name__ == "__main__":
    print("Hello World!")
    # logging.basicConfig()
    ip = input("Entre com IP ")
    port = input("Entre com a porta ")
    node = input("Entre com o ID do node ")
    client_dht = Client(ip, port, node)
    response = client_dht.send_hello()
    if response:
        server_dht = Server(ip, port, node)
        server_dht.start()
        client_dht.join_dht(response)
        server_dht.wait()

    else: 
        server_dht = Server(ip, port, node)
        server_dht.start()
        server_dht.wait()

    #client_dht.send_hello("localhost:", "50000")
