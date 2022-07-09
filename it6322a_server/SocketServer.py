import socket
import sys
import datetime

import pyvisa
import it6322a_server.config as config

class SocketServer:
    def __init__(self, ip_address: str, port: int, serial_number: str) -> None:
        self._ip_address = ip_address
        self._port = port
        self._serial_number = serial_number
        self._construct_socket_server()
        self._establish_connection_visa_hardware()
        self._print_msg(f'available at {ip_address}:{port}')

    def _print_msg(self, msg: any) -> None:
        # Blue
        pre = '\033[34m'
        post = '\033[0m'
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{pre}[{self.__class__.__name__}][{now}]{post} {msg}')
    
    def _establish_connection_visa_hardware(self) -> None:
        resource_man = pyvisa.ResourceManager()
        target_visa_address = None
        for address in resource_man.list_resources():
            if self._serial_number in address:
                target_visa_address = address
        if target_visa_address == None:
            raise ValueError(f"{self._serial_number} is not found")
        self._instr = resource_man.open_resource(target_visa_address)
        self._print_msg('_establish_connection_visa_hardware done')
    
    def _construct_socket_server(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._ip_address, self._port))
        self._socket.listen(1) # dont do parallel
        self._print_msg('_construct_socket_server done')

    def _throw_query(self, query: str) -> str:
        try:
            response = self._instr.query(query)
        except pyvisa.errors.VisaIOError as e:
            print(e, file=sys.stderr)
            response = str(e)
        except:
            response = "unknown error"
        return response
    
    def start(self) -> None:
        while True:
            client_socket, client_address = self._socket.accept()
            self._print_msg(f'connection from {client_address} established')
            received_query = client_socket.recv(config.buffer_size).decode(config.decoding_method)
            self._print_msg(f'query "{received_query}" received')
            response = self._throw_query(received_query)
            client_socket.send(response.encode(config.encoding_method))
            self._print_msg(f'response "{response.strip()}" sent')
            client_socket.close()