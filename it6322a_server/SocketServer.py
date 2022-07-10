import socket
import sys
import datetime
from loguru import logger
import pyvisa
import it6322a_server.config as config

class SocketServer:
    def __init__(self, ip_address: str, port: int, serial_number: str) -> None:
        self._ip_address = ip_address
        self._port = port
        self._serial_number = serial_number
        self._construct_socket_server()
        self._establish_connection_visa_hardware()
        logger.success(f'available at {ip_address}:{port}')
    
    def _establish_connection_visa_hardware(self) -> None:
        resource_man = pyvisa.ResourceManager()
        target_visa_address = None
        for address in resource_man.list_resources():
            if self._serial_number in address:
                target_visa_address = address
        if target_visa_address == None:
            raise ValueError(f"{self._serial_number} is not found")
        self._instr = resource_man.open_resource(target_visa_address)
        logger.success('done')
    
    def _construct_socket_server(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._ip_address, self._port))
        self._socket.listen(1) # dont do parallel
        logger.success('done')

    def _throw_query(self, query: str) -> str:
        try:
            response = self._instr.query(query)
        except pyvisa.errors.VisaIOError as e:
            logger.error(e, file=sys.stderr)
            response = str(e)
        except:
            response = "unknown error"
        return str(response)
        
    def _throw_write(self, write: str) -> None:
        try:
            response = self._instr.write(write)
        except pyvisa.errors.VisaIOError as e:
            logger.error(e, file=sys.stderr)
            response = str(e)
        except:
            response = "unknown error"
        return str(response)

    def _throw(self, msg):
        # msg examples : "wINST FIR"
        #              : "q*IDN?"
        if msg[0] == 'w':
            return self._throw_write(msg[1:])
        elif msg[0] == 'q':
            return self._throw_query(msg[1:])
        else:
            return "Error: query shoud be like 'q*IDN?' or 'rINST FIR'"

    def start(self) -> None:
        while True:
            client_socket, client_address = self._socket.accept()
            logger.debug(f'connection from {client_address} established')
            received_query = client_socket.recv(config.buffer_size).decode(config.decoding_method)
            logger.debug(f'query "{received_query}" received')
            response = self._throw(received_query)
            client_socket.send(response.encode(config.encoding_method))
            logger.debug(f'response "{response.strip()}" sent')
            client_socket.close()