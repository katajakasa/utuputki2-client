# -*- coding: utf-8 -*-

import json
from sock import Sock
import logging

log = logging.getLogger(__name__)


class Protocol(object):
    def __init__(self, url):
        self.url = url
        self.sock = Sock(url)

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
        self.sock.write(json.dumps(packet))

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
        self.sock.write(json.dumps(packet))

    def read(self):
        if not self.sock:
            return None

        d = self.sock.read()
        if d:
            return json.loads(d)
        return None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None



