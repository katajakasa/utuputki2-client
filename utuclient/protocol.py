# -*- coding: utf-8 -*-

import json
from sock import Sock
import logging
import socket
from websocket import WebSocketException

log = logging.getLogger(__name__)


class Protocol(object):
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.sock = Sock(url)
        self.reconnect()

    def reconnect(self):
        try:
            self.sock.reconnect()
            self.write_msg('login', {'token': self.token})
        except socket.error:
            log.warn(u"Reconnect failed ...")
        except WebSocketException:
            log.warn(u"Reconnect failed ...")

    def write_error(self, mtype, message, code, query=None):
        if not self.sock:
            return
        packet = {
            'error': 1,
            'data': {
                'code': code,
                'message': message,
            },
            'type': mtype,
        }
        if query:
            packet['query'] = query

        try:
            self.sock.write(json.dumps(packet))
        except socket.error:
            self.reconnect()
        except WebSocketException, e:
            self.reconnect()
            log.info(u"Connection error: %s", str(e))

    def write_msg(self, mtype, data, query=None):
        if not self.sock:
            return
        packet = {
            'error': 0,
            'data': data,
            'type': mtype,
        }
        if query:
            packet['query'] = query
        log.info(u"Writing %s", json.dumps(packet))

        try:
            self.sock.write(json.dumps(packet))
        except socket.error:
            self.reconnect()
        except WebSocketException, e:
            self.reconnect()
            log.info(u"Connection error: %s", str(e))

    def read(self):
        if not self.sock:
            return None

        d = None
        try:
            d = self.sock.read()
        except socket.error:
            self.reconnect()
        except WebSocketException, e:
            self.reconnect()
            log.info(u"Connection error: %s", str(e))

        if d:
            log.info(u"Read %s", d)
            return json.loads(d)
        return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None



