from __future__ import print_function
from datetime import datetime, timezone

import logging
import grpc

from dht_client import Client

from database import create_tables
from database import create_database
from database import resources as RS
from protos import meu_qoelho_mq_pb2
from protos import meu_qoelho_mq_pb2_grpc

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel("localhost:50051") as channel:
        create_tables.create_tables()
        res_canal1 = RS.insert_channel("Canal1", "SIMPLES")
        if res_canal1["status"] == 0:
            response = "Canal1 criado com sucesso"
        else:
            response = "Erro ao criar canal."
        print(response)
        res_canal2 = RS.insert_channel("Canal2", "MULTIPLO")
        if res_canal2["status"] == 0:
            response = "Canal2 criado com sucesso"
        else:
            response = "Erro ao criar canal."
        print(response)

        

if __name__ == "__main__":
    logging.basicConfig()
    run()

