# -*- coding: utf-8 -*-

from gi.repository import GLib as glib
import logging
from window import Window
from player import Player
from protocol import Protocol

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, url, token, video_url):
        self.video_url = video_url
        self.proto = Protocol(url)
        self.proto.write_msg('login', {'token': token})
        self.window = Window()
        self.player = Player(self.window)
        self.is_running = False

        self.remote_status = 0
        self.remote_seek = None

    def on_unknown_msg(self, query, data, error):
        log.info("Unknown msg: {}: {}".format(query, data))

    def on_player_msg(self, query, data, error):
        if error == 1:
            log.warn("Server responded: {}".format(data['message']))
            self.close()
            return

        if query == 'set_status':
            self.remote_status = data.get('status')
            return

        if query == 'seek':
            self.remote_seek = data.get('time')
            return

        if query == 'source':
            self.player.set_src(data.get('url'))
            self.remote_status = 1
            self.player.play()
            return

    def on_login_msg(self, query, data, error):
        if error == 1:
            log.warn("Server responded: {}".format(data['message']))
            self.close()
            return

        log.info("Logged in as {}".format(data['name']))

    def run_checks(self):
        if not self.is_running:
            return

        # Handle incoming messages
        m = 0
        d = self.proto.read()

        # Only handle a few packages at a time, and only if the previous package returns something.
        while m < 10 and d:
            if d:
                # Handle this message
                mtype = d.get('type', 'unknown')
                query = d.get('query')
                data = d.get('data', {})
                error = d.get('error', 0) == 1
                cbs = {
                    'login': self.on_login_msg,
                    'playerdev': self.on_player_msg,
                    'unknown': self.on_unknown_msg,
                }
                cbs[mtype if mtype in cbs else 'unknown'](query, data, error)

                # Read next
                d = self.proto.read()
            m += 1

        # If video is stopped and remote didn't request it, it was probably because the video has ended.
        if not self.remote_status == 0 and self.player.is_stopped():
            self.proto.write_msg('playerdev', {'status': 0}, 'status_change')
        elif self.remote_status != 0 and not self.player.is_stopped():
            self.player.stop()

        # Check if we need to pause
        if self.remote_status == 2 and not self.player.is_paused():
            self.player.pause()

        # If not playing and remote requests it, do so
        if self.remote_status == 1 and not self.player.is_playing():
            self.player.play()

        # Continue listening
        glib.timeout_add(50, self.run_checks)

    def run(self):
        self.is_running = True
        glib.timeout_add(100, self.run_checks)
        self.window.run()

    def close(self):
        if self.is_running:
            self.is_running = False
            self.player.stop()
            self.window.close()
            self.proto.close()

