# -*- coding: utf-8 -*-

import websocket
import logging

log = logging.getLogger(__name__)


class Sock(object):
    def __init__(self, url):
        self.url = url
        self.ws = websocket.WebSocket()
        self.ws.connect(url)

    def reconnect(self):
        self.ws.connect(self.url)

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
