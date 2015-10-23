# -*- coding: utf-8 -*-

import json
from sock import Sock
import logging
import socket

log = logging.getLogger(__name__)


class Protocol(object):
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.sock = Sock(url)
        self.write_msg('login', {'token': token})

    def reconnect(self):
        try:
            self.sock.reconnect()
            self.write_msg('login', {'token': self.token})
        except socket.error:
            log.warn("Reconnect failed ...")

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
        log.info("Writing {}".format(json.dumps(packet)))

        try:
            self.sock.write(json.dumps(packet))
        except socket.error:
            self.reconnect()

    def read(self):
        if not self.sock:
            return None

        d = None
        try:
            d = self.sock.read()
        except socket.error:
            self.reconnect()

        if d:
            log.info("Read {}".format(d))
            return json.loads(d)
        return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None



