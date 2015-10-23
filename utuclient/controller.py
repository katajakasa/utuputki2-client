# -*- coding: utf-8 -*-

from gi.repository import GLib as glib
import logging
import os
from window import Window
from player import Player
from protocol import Protocol

log = logging.getLogger(__name__)


class Controller(object):
    def __init__(self, url, token, fullscreen):
        self.proto = Protocol(url)
        self.proto.write_msg('login', {'token': token})
        self.window = Window(fullscreen)
        self.player = Player(self.window, self.player_finished)

        self.is_running = False
        self.remote_status = 0
        self.remote_seek = None
        self.remote_source = None
        self.remote_poke = False
        self.waiting = True

    def player_finished(self, player):
        self.remote_poke = True

    def on_unknown_msg(self, query, data, error):
        log.info("Unknown msg: {}: {}".format(query, data))

    def write_status(self, status, end=False):
        msg = {'status': status}
        if end:
            msg['end'] = True
        self.proto.write_msg('playerdev', msg, 'status_change')

    def on_player_msg(self, query, data, error):
        if error == 1:
            log.warn("Server responded: {}".format(data['message']))
            return

        self.waiting = False

        # Poke message from server: Something happened on the server that might interest us.
        if query == 'poke':
            self.remote_poke = True
            return

        # Sets our status (stopped, playing, paused)
        if query == 'set_status':
            self.remote_status = data.get('status')
            return

        # Returns our status
        if query == 'get_status':
            self.write_status(self.player.status())
            return

        # Seek to position (in seconds)
        if query == 'seek':
            self.remote_seek = data.get('time')
            return

        # Set our video source
        if query == 'source':
            self.remote_source = data.get('url')
            return

    def on_login_msg(self, query, data, error):
        if error == 1:
            log.warn("Server responded: {}".format(data['message']))
            self.close()
            return

        # Okay, we got in. Let's get on with it.
        log.info("Logged in as {}".format(data['name']))

        # Send initial status
        self.write_status(0, True)

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

        # If we are settings a remote source, go ahead
        if self.remote_source:
            if self.player.is_playing():
                self.player.stop()

            # Set up a new player
            self.player.set_src(self.remote_source)
            self.player.play()

            # Set up statuses
            self.waiting = False
            self.remote_status = 1
            self.write_status(1)

            # Log and clear remote op
            log.info("Switching to {}".format(self.remote_source))
            self.remote_source = None
            self.remote_poke = False
        elif self.remote_poke:
            log.info("Poked.")
            self.write_status(0, True)
            self.remote_poke = False

        # If we need to seek, do so now
        if (self.player.is_playing() or self.player.is_paused()) and self.remote_seek:
            self.player.seek(self.remote_seek)
            log.info("Seeking to {}".format(self.remote_source))
            self.remote_seek = None

        # If we are not resting, do something ...
        if not self.waiting:
            # If video is stopped and remote didn't request it, it was probably because the video has ended.
            if self.remote_status == 0 and not self.player.is_stopped():
                self.player.stop()
                self.write_status(0)
                log.info("Status = Stopped")

            # Check if we need to pause
            if self.remote_status == 2 and not self.player.is_paused():
                self.player.pause()
                self.write_status(2)
                log.info("Status = Paused")

            # If not playing and remote requests it, do so
            if self.remote_status == 1 and not self.player.is_playing():
                self.player.play()
                self.write_status(1)
                log.info("Status = Playing")

        # Continue listening
        glib.timeout_add(50, self.run_checks)

    def run(self):
        self.is_running = True
        glib.timeout_add(100, self.run_checks)
        self.window.run()

    def close(self):
        if self.is_running:
            self.is_running = False
            if self.player:
                self.player.stop()
            self.window.close()
            self.proto.close()

