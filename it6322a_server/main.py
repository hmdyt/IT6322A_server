import it6322a_server.config as config
from it6322a_server.SocketServer import SocketServer

def main():
    socket_server = SocketServer(
        config.server_ip,
        config.server_port,
        config.hardware_serial_number
    )
    socket_server.start()

if __name__ == '__main__':
    main()