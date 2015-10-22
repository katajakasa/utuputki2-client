# -*- coding: utf-8 -*-

import json
from sock import Sock


class Protocol(object):
    def __init__(self, url, token, on_msg=None):
        self.url = url
        self.token = token
        self.sock = Sock(url)

    def write_error(self, mtype, message, code, query=None):
        packet = {
            'error': 1,
            'message': {
                'code': code,
                'message': message,
            },
            'type': mtype,
        }
        if query:
            packet['query'] = query
        self.sock.write(json.dumps(packet))

    def write_msg(self, mtype, data, query=None):
        packet = {
            'error': 0,
            'message': data,
            'type': mtype,
        }
        if query:
            packet['query'] = query
        self.sock.write(json.dumps(packet))

    def read(self):
        d = self.sock.read()
        if d:
            return json.loads(d)
        return None

    def close(self):
        self.sock.close()
        self.sock = None



