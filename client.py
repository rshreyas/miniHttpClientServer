#!/usr/bin/env python3
'''
 Runs the HTTP Client application.

 This Python wrapper was written by Shreyas Ramesh <shreyas2@vt.edu>

 The program REQUIRES basic Python3 and packages -- `sockets` and `sys`
'''
# ----------------- #
#  Generic Imports  #
# ----------------- #

# Client Version
__version__ = "1.0.0"

import socket
import sys


class Client:
    """
    Client HTTP application for file transfer.
    """

    def __init__(self, user_def_socket=None):
        if user_def_socket is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = user_def_socket

        self.CHUNK_SIZE = 4096
        self.HTTP_VERSION = 1.0
        self.CRLF = "\r\n\r\n"


    def _connect(self, remote_server_name, remote_server_port):
        # Three-way handshake init
        try:
            remote_server_IP = socket.gethostbyname(remote_server_name)
            self.sock.connect((remote_server_IP, remote_server_port))

        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
            sys.exit()

        except socket.error:
            print("Couldn't connect to server")
            sys.exit()


    def _request_one_file(self, file_name, save_file_path):
        total_bytes_sent = 0

        HTTP_GET_REQ = 'GET /{0} HTTP/{1}{2}'.format(file_name,
                                                     self.HTTP_VERSION,
                                                     self.CRLF)
        MSGLEN = len(HTTP_GET_REQ)

        while total_bytes_sent < MSGLEN:
            sent_now = self.sock.send(HTTP_GET_REQ[total_bytes_sent:].encode())
            if sent_now == 0:
                raise RuntimeError("Socket connection broken")
            total_bytes_sent = total_bytes_sent + sent_now

        print("File request sent successfully")

        # Request for file to server completed. Waiting for file.
        self._receive_one_file(save_file_path)

        # Timely release of resources and close
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


    def _receive_one_file(self, save_file_path):
        file_contents = []
        while True:
            curr_chunk = self.sock.recv(self.CHUNK_SIZE)
            if curr_chunk:
                file_contents.append(curr_chunk.decode())
            else:
                break

        file_content_string = ''.join(file_contents)

        data = file_content_string
        headers = data.split(self.CRLF, 1)[0]
        request_line = headers.split('\n')[0]
        response_code = request_line.split()[1]
        headers = headers.replace(request_line, '')

        body = '\n'.join(data.replace(headers, '').replace(request_line, '').split('\n')[2:])

        if response_code == "200":
            print("Response OK...writing to file")
            with open(save_file_path, 'w') as save_file:
                save_file.write(body)
        elif response_code == "400":
            raise RuntimeError("Request format incorrect")
        elif response_code == "404":
            raise RuntimeError("File not found in server")
            sys.exit()
        else:
            raise RuntimeError("Unknown error occured")


    def file_query(self):
        host_name = input("Enter Hostname ")
        port_no = int(input("Enter Server Port "))

        self._connect(host_name, port_no)

        print("Connection to {} at port {} established".format(host_name, port_no))

        file_name = input("Enter file name to retrieve ")
        save_file_path = input("Enter location to store HTML file ")

        if not file_name:
            raise RuntimeError("Filename empty. Retry")

        self._request_one_file(file_name=file_name, save_file_path=save_file_path)

# ------------------------------ #
#  Pythonic Interface Functions  #
# ------------------------------ #

if __name__ == '__main__':
    client = Client()
    client.file_query()
