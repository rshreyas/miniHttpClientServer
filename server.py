#!/usr/bin/env python3
'''
 Runs the HTTP Server application.

 This Python wrapper was written by Shreyas Ramesh <shreyas2@vt.edu>

 The program REQUIRES basic Python3 and package -- `sockets` and `os`
'''
# ----------------- #
#  Generic Imports  #
# ----------------- #

# Server Version
__version__ = "1.0.0"

import socket
import os


class Server:
    """
    Server HTTP application for file transfer.
    """

    def __init__(self, host_name='localhost', port_no=8080):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_name = host_name
        self.port_no = port_no
        self.sock.bind((self.host_name, self.port_no))
        self.sock.listen(1)  # Do not queue any requests
        self.CHUNK_SIZE = 4096
        self.HTTP_VERSION = 1.0
        self.CRLF = "\r\n\r\n"
        self.NUM_CONNECTIONS_SERVED = 0


    def _error_clean_close(self, client_connection, error_message='404 Not Found'):
        code = error_message.split()[0]
        message = ' '.join(error_message.split()[1:])
        client_connection.send('HTTP/{0} {1} {2}{3}'.format(self.HTTP_VERSION,
                                                            code, message,
                                                            self.CRLF).encode())
        self.NUM_CONNECTIONS_SERVED += 1
        print("{0} connections served. Accepting new client...".format(self.NUM_CONNECTIONS_SERVED))


    def listen_for_clients(self):
        print("Server Initialized...looking for clients to connect")
        while True:
            client_connection, address = self.sock.accept()
            try:
                message = client_connection.recv(self.CHUNK_SIZE).decode().split('\n')
                request_type, filename, http_version_formatted = message[0].split()
                if request_type != "GET" or 'HTTP/{0}'.\
                                            format(self.HTTP_VERSION) != http_version_formatted:
                    self._error_clean_close(client_connection, '400 Bad Request')
                    self.NUM_CONNECTIONS_SERVED += 1
                    print("{0} connections served. Accepting new client...".format(self.NUM_CONNECTIONS_SERVED))
                    client_connection.close()
                    continue

                filename = filename[1:]
                f = open(filename)
                data = f.read()
                f.close()

                content_len = 'Content-Length: {0}'.format(os.stat(filename).st_size)

                client_connection.send('HTTP/{0} {1} {2}\n{3}{4}'.format(self.HTTP_VERSION,
                                                                    '200', 'OK', content_len,
                                                                    self.CRLF).encode())

                # Send the content of the requested file to the client
                for i in range(0, len(data)):
                    client_connection.send(data[i].encode())

                self.NUM_CONNECTIONS_SERVED += 1
                print("{0} connections served. Accepting new client...".format(self.NUM_CONNECTIONS_SERVED))
                client_connection.close()

            except FileNotFoundError:
                # Send response message for file not found
                self._error_clean_close(client_connection, '404 Not Found')
                # Close client socket
                client_connection.close()


# ------------------------------ #
#  Pythonic Interface Functions  #
# ------------------------------ #


if __name__ == '__main__':
    server = Server()
    server.listen_for_clients()
