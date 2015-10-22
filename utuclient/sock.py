# -*- coding: utf-8 -*-

import websocket


class Sock(object):
    def __init__(self, url):
        self.ws = websocket.WebSocket()
        self.ws.connect(url)

    def read(self):
        self.ws.sock.settimeout(0.1)
        try:
            return self.ws.recv()
        except websocket.WebSocketTimeoutException:
            return None

    def write(self, data):
        self.ws.sock.settimeout(1)
        return self.ws.send(data)

    def close(self):
        self.ws.close()
        self.ws = None
