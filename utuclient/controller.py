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
        self.proto = Protocol(url, token)
        self.window = Window(fullscreen)

        self.is_running = False
        self.to_status = 0
        self.current_status = 0
        self.got_poke = False

        self.seek_to = None
        self.source_to = None

        # Get the ad image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stopped_image_url = "file://"+os.path.join(base_dir, "resources/standby.png")
        self.maintenance_image_url = "file://"+os.path.join(base_dir, "resources/maintenance.png")

        # Show image at start
        self.player = Player(self.window,
                             self.stopped_image_url,
                             self.player_finished,
                             self.player_error,
                             mode=Player.IMAGE)

    def player_finished(self):
        if self.to_status != 4:
            self.to_status = 0

    def player_error(self, error):
        if self.to_status != 4:
            self.to_status = 0

    def on_unknown_msg(self, query, data, error):
        log.info(u"Unknown msg: {}: {}".format(query, data))

    def write_status(self, status):
        self.proto.write_msg('playerdev', {'status': status}, 'status_change')

    def on_player_msg(self, query, data, error):
        if error == 1:
            log.warn("Server responded: {}".format(data['message']))
            return

        # Poke message from server: Something happened on the server that might interest us.
        if query == 'poke':
            self.got_poke = True
            return

        # Sets our status (stopped, playing, paused)
        if query == 'set_status':
            self.to_status = data.get('status')
            return

        # Seek to position (in seconds)
        if query == 'seek':
            self.seek_to = data.get('time')
            return

        # Set our video source
        if query == 'source':
            self.source_to = data.get('url')
            self.to_status = 1
            return

    def on_login_msg(self, query, data, error):
        if error == 1:
            log.warn("Server responded: {}".format(data['message']))
            self.close()
            return

        # Okay, we got in. Let's get on with it.
        log.info("Logged in as {}".format(data['name']))

        # Send initial status
        self.write_status(self.current_status)

    def run_checks(self):
        if not self.is_running:
            return

        timeout = 100

        # Handle incoming messages
        d = self.proto.read()

        # Handle all the messages on queue
        while d:
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

        # If we are settings a remote source, go ahead
        if self.source_to and self.to_status == 1:
            # If we are currently playing, stop.
            if self.player:
                self.player.close()

            # Set up statuses
            self.current_status = 1
            self.write_status(self.current_status)

            # Set up a new player
            self.player = Player(self.window, self.source_to, self.player_finished, self.player_error)
            self.player.play()

            # Log and clear remote op
            log.info(u"Switching to {}".format(self.source_to))
            self.source_to = None

            # Timeout and quit here. We're waiting.
            timeout = 1000

        # Poke the server back, hard. MAKE it give us videos.
        if self.got_poke:
            self.got_poke = False

            # If we are stopped currently, and we're not going to start anything, send status
            if self.to_status == 0 and self.current_status == 0:
                self.write_status(self.current_status)

                # Timeout. We're waiting.
                timeout = 1000

        # If we need to seek, do so now. Only when paused or playing.
        if self.current_status != 0 and self.seek_to:
            self.player.seek(self.seek_to)
            log.info(u"Seeking to %d", self.seek_to)
            self.seek_to = None

        # Check if we need to stop
        if self.current_status != 0 and self.to_status == 0:
            if self.player:
                self.player.close()
            self.write_status(0)
            self.current_status = 0
            self.player = Player(self.window,
                                 self.stopped_image_url,
                                 self.player_finished,
                                 self.player_error,
                                 mode=Player.IMAGE)
            log.info(u"Status = Stopped")

        # Check if we need to pause
        if self.current_status == 1 and self.to_status == 2:
            self.player.pause()
            self.write_status(2)
            self.current_status = 2
            log.info(u"Status = Paused")

        # If paused and remote requests start, do so
        elif self.current_status == 2 and self.to_status == 1 and self.player:
            self.player.play()
            self.write_status(1)
            self.current_status = 1
            log.info(u"Status = Playing")

        # If stopped and remote requests start, do so
        elif self.current_status == 0 and self.to_status == 1:
            self.write_status(0)
            self.current_status = 0
            log.info(u"Status = Stopped")

        # If maintenance and remote requests start, do so
        elif self.current_status == 4 and self.to_status == 1:
            self.write_status(0)
            self.current_status = 0
            log.info(u"Status = Stopped")

        # Maintenance
        if self.current_status != 4 and self.to_status == 4:
            if self.player:
                self.player.close()
            self.write_status(4)
            self.current_status = 4
            self.player = Player(self.window,
                                 self.maintenance_image_url,
                                 self.player_finished,
                                 self.player_error,
                                 mode=Player.IMAGE)
            timeout = 100

        # Continue listening
        glib.timeout_add(timeout, self.run_checks)

    def run(self):
        self.is_running = True
        glib.timeout_add(100, self.run_checks)
        self.window.run()

    def close(self):
        if self.is_running:
            self.is_running = False
            if self.player:
                self.player.close()
            self.window.close()
            self.proto.close()

