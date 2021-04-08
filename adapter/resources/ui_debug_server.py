'''
    Simple socket server using threads
'''

import socket
import threading

import hou


HOST = ''
PORT = 8887


command = ''


def _exec():
    exec(command)
    hou.ui.removeEventLoopCallback(_exec)


def server_start():
    global command

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)

    while True:
        client, _ = s.accept()
        try:
            command = client.recv(4096)
            if command:
                hou.ui.addEventLoopCallback(_exec)
        except SystemExit:
            result = self.encode('SERVER: Shutting down...')
            if result:
                client.send(result)
            raise
        finally:
            client.close()


t = threading.Thread(None, server_start)
t.setDaemon(True)
t.start()
