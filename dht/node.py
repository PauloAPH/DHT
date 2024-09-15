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
import time
import hashlib
import grpc
import logging

from google.protobuf import empty_pb2


from protos import dht_pb2
from protos import dht_pb2_grpc


def hash_helper(ip, port):
    id = int.from_bytes(hashlib.sha256((ip+port).encode('utf-8')).digest()[:4], 'little')
    print(id)
    return id

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
        print("NODE: "+  str(self.id))
        print("Next node id: " + str(self.n_id) + " adress: "+ self.n_ip + self.n_port)
        print("Previuos node id: " + str(self.p_id) + " adress: "+ self.p_ip + self.p_port)

    def get_params(self):
        return {'ip' : self.ip, 
                'port' : self.port, 
                'id' : self.id, 
                'n_id' : self.n_id, 
                'n_ip' : self.n_ip, 
                'n_port' : self.n_port, 
                'p_id' : self.p_id, 
                'p_ip' : self.p_ip, 
                'p_port' : self.p_port}
        
    def hello(self, request, context):
        print("Respondendo node " + request.port)
        return dht_pb2.Join(ip = "localhost:", port = self.port, id = int(self.id))
    
    def try_to_join(self, request, context):
        print("No " + request.port + " tentando entrar na rede")
        if self.p_id == 0:
            print("Enviando resposta")
            client_dht = Node(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.ip, self.port, self.id, self.ip, self.port)
            self.p_id = request.id
            self.p_ip =  request.ip
            self.p_port = request.port
            self.print_all()

        elif request.id > self.p_id and request.id < self.id:
            print("Enviando resposta 2")
            client_dht = Node(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.ip, self.port, self.p_id, self.p_ip, self.p_port)
            self.p_id = request.id
            self.p_ip =  request.ip
            self.p_port = request.port           

        # p = 50 self = 30 r = 40,
        elif self.p_id > request.id and request.id < self.id:
            print("Enviando resposta 3")
            client_dht = Node(request.ip, request.port, request.id)
            client_dht.join_response(self.id, self.ip, self.port, self.p_id, self.p_ip, self.p_port)
            self.p_id = request.id
            self.p_ip =  request.ip
            self.p_port = request.port  

        else:
            print("Encaminhando req")
            client_dht = Node(request.ip, request.port, request.id)
            client_dht.join_dht(self.n_ip, self.n_port)
        return empty_pb2.Empty()

    
    def join_response(self, request, context):
        print("Resposta de entrada na rede recebida")
        self.n_id  = request.next_id 
        self.n_ip = request.next_ip
        self.n_port = request.next_port 
        self.p_id  = request.pre_id 
        self.p_ip = request.pre_ip
        self.p_port = request.pre_port 
        client_dht = Node(self.ip, self.port, self.id)
        client_dht.update_previous(self.p_ip, self.p_port, self.p_id)
        return empty_pb2.Empty()
    
    def uptade_next_node_params(self, request, context):
        print("Recebendo pedido de atualização")
        self.n_id  = request.id
        self.n_ip = request.ip 
        self.n_port = request.port
        return empty_pb2.Empty()
    
    def uptade_previuos_node_params(self, request, context):
        print("Recebendo pedido de atualização")
        self.p_id  = request.id
        self.p_ip = request.ip 
        self.p_port = request.port
        return empty_pb2.Empty()


class Node():
    def __init__(self, ip, port, id):
        self.ip = ip
        self.port = port
        self.id = id
        self.params_map = {'ip' : ip, 
                           'port' : port, 
                           'id' : id, 
                           'n_id' : 0, 
                           'n_ip' : "", 
                           'n_port' : "", 
                           'p_id' : 0, 
                           'p_ip' : "", 
                           'p_port' : ""}

        

    def update_params(self):
        self.params_map = self.servicer.get_params()

  

    def print_stat(self):
        self.servicer.print_all()

    def start(self):
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.servicer = DHTServicer(self.ip, self.port, self.id)

        dht_pb2_grpc.add_DHTServicer_to_server(self.servicer, self.grpc_server)

        self.grpc_server.add_insecure_port("[::]:" + self.port)
        self.grpc_server.start()

    def wait(self):
        self.grpc_server.wait_for_termination()
        

    def update_previous(self, p_ip, p_port, p_id):
        print("Atualizando anterior")
        with grpc.insecure_channel(p_ip + p_port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            node = dht_pb2.Join(ip = self.ip, port = self.port, id = self.id)
            stub.uptade_next_node_params(node)

    def send_hello(self):
        with open("/home/paulo/sist_distribuidos/DHT/dht/dhtList.txt", "r") as file:
            ports = file.readlines()
            ports = [name.strip() for name in ports]  
            ok = 0
            for port in ports:
                with grpc.insecure_channel(port) as channel:
                    stub = dht_pb2_grpc.DHTStub(channel)
                    node = dht_pb2.Join(ip = "localhost:", port = self.port, id = self.id)
                    try:
                        response = stub.hello(node)
                    except grpc.RpcError as rpc_error:
                        print(f"Tentando o prox host")
                    else:
                        if response.port:
                            port_ok = port
                            ok = 1
                            break
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
            stub.try_to_join(node)


    def join_response(self, n_id, n_ip, n_port, p_id, p_ip, p_port):
        print(self.ip + self.port)
        with grpc.insecure_channel(self.ip + self.port) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            join_data = dht_pb2.JoinOk(next_id = n_id, next_ip = n_ip, next_port = n_port, pre_id = p_id, pre_ip = p_ip, pre_port = p_port)
            stub.join_response(join_data)

    def leave_dht(self):
        print("Saindo da rede DHT")
        self.update_params()
        to_previous = dht_pb2.Join(ip = self.params_map['n_ip'], port = self.params_map['n_port'], id = self.params_map['n_id'])
        to_next = dht_pb2.Join(ip = self.params_map['p_ip'], port = self.params_map['p_port'], id = self.params_map['p_id'])
        with grpc.insecure_channel(self.params_map['p_ip'] + self.params_map['p_port']) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            stub.uptade_next_node_params(to_previous)
        with grpc.insecure_channel(self.params_map['n_ip'] + self.params_map['n_port']) as channel:
            stub = dht_pb2_grpc.DHTStub(channel)
            stub.uptade_previuos_node_params(to_next)


if __name__ == "__main__":    

    # ip = input("Entre com IP ")
    ip = "localhost:"
    port  = input("Entre com a porta ")
    id = hash_helper(ip, port)
    #id = int(input("Entre com o ID do node "))

    client_dht = Node(ip, port, id)
    response = client_dht.send_hello()

    if response:
        client_dht.start()
        res = response.split(":")
        client_dht.join_dht("localhost:", res[1])
    else: 
        client_dht.start()

    try:
        while True:
            time.sleep(20)
            client_dht.print_stat()
    except KeyboardInterrupt:
        client_dht.leave_dht()
        


