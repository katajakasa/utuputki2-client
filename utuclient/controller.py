# -*- coding: utf-8 -*-

from gi.repository import GLib as glib

from window import Window
from player import Player
from protocol import Protocol


class Controller(object):
    def __init__(self, url, token, video_url):
        self.video_url = video_url
        self.proto = Protocol(url, token)
        self.proto.write_msg('login', {'token': token})
        self.window = Window()
        self.player = Player(self.window)
        self.is_running = False

    def run_checks(self):
        if not self.is_running:
            return

        d = self.proto.read()
        if d:
            print d

        glib.timeout_add(10, self.run_checks)

    def run(self):
        self.is_running = True
        glib.timeout_add(100, self.run_checks)
        self.window.run()

    def close(self):
        self.is_running = False
        self.window.close()
        self.player.stop()
        self.proto.close()

