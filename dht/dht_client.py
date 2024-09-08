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
    def create_user(stub, id, password):
        user = dht_pb2.Credentials(id = id, password = password)
        res = stub.Register(user)
        if res.status == 0:
            return "Usuario criado com sucesso"
        else:
            return "Erro ao criar usuario"

    def create_channel_request(stub, name, tipo):
        channel = dht_pb2.Channels()
        channel.name = name
        if tipo == "Simples":
            channel.tipo = dht_pb2.Tipo.SIMPLES
        elif tipo == "Multiplo":
            channel.tipo = dht_pb2.Tipo.MULTIPLO
        res = stub.CreateChannel(channel)
        if res.status == 0:
            return "Canal criado com sucesso"
        else:
            return "Erro ao criar usuario"

    def delete_channel_request(stub, name):
        channel = dht_pb2.Channels(name = name)
        res = stub.DeleteChannel(channel)
        if res.status == 0:
            return "Canal deletado com sucesso"
        else:
            return "Erro ao deletar canal"        

    def list_channels(stub):
        channel_out = dht_pb2.Channels(name = "Canal1")
        channels = stub.ListChannels(channel_out)
        response = []
        for channel in channels:
            tipo = dht_pb2.Tipo.Name(channel.tipo)
            response.append(channel.name +  " Tipo: " + tipo)
        return response

    def publish_message(stub, data_in, channel_in):
        msg = dht_pb2.Message(data = data_in, channel = channel_in)
        res = stub.PublishMessage(msg)
        print(res.response)

    def subscribe_to_channel(stub, cred, channel):
        subs = dht_pb2.Subscriber(credentials = cred, channel = channel)
        res = stub.SubscribeToChannel(subs)
        if res.status == 0:
            return res.response
        else: 
            return "ERROR: " + res.response

    def consult_messages_in_channel(stub):
        cred = dht_pb2.Credentials(id = "Paulo", password = "123456")
        sub = dht_pb2.Subscriber(credentials = cred, channel = "Canal2")
        qtd = stub.ConsultNumberOfMessages(sub)
        print(qtd)

    def get_messages_from_subscrition(stub, sub):
        res = stub.GetMessageFromChannel(sub)
        response = []
        for r in res:
            response.append(r.response)
        return response


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = dht_pb2_grpc.DHTStub(channel)

if __name__ == "__main__":
    logging.basicConfig()
    run()
