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

import asyncio
from concurrent import futures
import time

import grpc
import logging

from google.protobuf import empty_pb2


from protos import dht_pb2
from protos import dht_pb2_grpc

class DHTServicer(dht_pb2_grpc.DHTServicer):
    """Provides methods that implement functionality of DHT server."""

    def __init__(self, ip, port, id):
        print("Server runnig: Hello World!")
        self.ip = ip
        self.port = port
        self.id = id

        self.n_id =  0
        self.n_ip =  ""
        self.n_port = ""
        self.p_id = 0
        self.p_ip =  ""
        self.p_port = ""

    def print_all(self):
        print("Next node id: " + str(self.n_id) + " Next node adress: "+ self.n_ip + self.n_port)
        print("Previuos node id: " + str(self.p_id) + " Previuos node adress: "+ self.p_ip + self.p_port)
        

    def Hello(self, request, context):
        print("respondendo node " + request.port)
        return dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
    
    def Try_Join(self, request, context):
        print("No " + request.port + " tentando entrar na rede")
        if self.p_id == 0:
            print("Enviando resposta")
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.ip, self.port, self.id, self.ip, self.port)
            self.p_id = request.id
            self.p_ip =  request.ip
            self.p_port = request.port
            self.print_all()

        elif request.id > self.p_id and request.id < self.id:
            print("Enviando resposta 2")
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.ip, self.port, self.p_id, self.p_ip, self.p_port)
            self.p_id = request.id
            self.p_ip =  request.ip
            self.p_port = request.port           

        elif  self.p_id > self.id and request.id > self.id:
            print("Enviando resposta 3")
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.ip, self.port, self.p_id, self.p_ip, self.p_port)
            self.p_id = request.id
            self.p_ip =  request.ip
            self.p_port = request.port  

        else:
            print("Encaminhando req")
            client_dht = Client(request.ip, request.port, request.id)
            client_dht.join_dht(self.n_ip, self.n_port)
        return empty_pb2.Empty()

    
    def Join_ok(self, request, context):
        print("Resposta de entrada na rede recebida")
        self.n_id  = request.next_id 
        self.n_ip = request.next_ip
        self.n_port = request.next_port 
        self.p_id  = request.pre_id 
        self.p_ip = request.pre_ip
        self.p_port = request.pre_port 
        client_dht = Client(self.ip, self.port, self.id)
        client_dht.update_previous(self.p_ip, self.p_port, self.p_id)
        return empty_pb2.Empty()
    
    def Update_Next(self, request, context):
        print("Recebendo pedido de atualização")
        self.n_id  = request.id
        self.n_ip = request.ip 
        self.n_port = request.port
        return empty_pb2.Empty()

class Client():
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id

    def update_previous(self, p_ip, p_port, p_id):
        print("Atualizando anterior")
        with grpc.insecure_channel(p_ip + p_port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            node = dht_pb2.Join(ip = self.ip, port = self.port, id = self.id)
            stub.Update_Next(node)

    def send_hello(self):
        with open("/home/paulo/sist_distribuidos/DHT/dht/dhtList.txt", "r") as file:
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

    def join_dht(self, ip, port):
        print(ip+port)
        with grpc.insecure_channel(ip+port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            node = dht_pb2.Join(ip = "localhost:", port = self.port, id = self.id)
            stub.Try_Join(node)


    def join_response(self, n_id, n_ip, n_port, p_id, p_ip, p_port):
        print(self.ip + self.port)
        with grpc.insecure_channel(self.ip + self.port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            join_data = dht_pb2.JoinOk(next_id = n_id, next_ip = n_ip, next_port = n_port, pre_id = p_id, pre_ip = p_ip, pre_port = p_port)
            stub.Join_ok(join_data)




class Server():   
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.servicer = DHTServicer(self.ip, self.port, self.id)
        dht_pb2_grpc.add_DHTServicer_to_server( self.servicer, self.grpc_server)
        self.grpc_server.add_insecure_port("[::]:" + self.port)


    def print_stat(self):
        self.servicer.print_all()

    def start(self):
        self.grpc_server.start()

    def wait(self):
        self.grpc_server.wait_for_termination()
        


if __name__ == "__main__":    
    # ip = input("Entre com IP ")
    ip = "localhost:"
    port  = input("Entre com a porta ")
    node = int(input("Entre com o ID do node "))
    client_dht = Client(ip, port, node)
    response = client_dht.send_hello()
    if response:
        server_dht = Server(ip, port, node)
        server_dht.start()
        res = response.split(":")
        client_dht.join_dht("localhost:", res[1])
        # server_dht.wait()

    else: 
        server_dht = Server(ip, port, node)
        server_dht.start()
        # server_dht.wait()

    while 1:
        time.sleep(50)
        server_dht.print_stat()
        


