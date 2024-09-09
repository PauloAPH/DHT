# Projeto da disciplina MCTA025-13-Sistemas Distribuidos UFABC - 2024
## Autores: 
- Paulo Alexandre Pizará Hayashida RA: 11201722652
- Igor Ladeia de Freitas RA: 11201922180

### Comandos Terminal
#### Instalar protobuf compiler
```
 sudo apt install protobuf-compiler
```
### Python
#### Comando para instalar gRPC tools
 ```
 pip install grpcio-tools 
```
#### Comando para instalar psycopg2
 ```
 pip install psycopg2-binary
```
#### Gerar protobuf e stubs em python
```
 python3 -m grpc_tools.protoc -I. --python_out=.  --grpc_python_out=.  protos/dht.proto
```
