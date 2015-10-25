# -*- coding: utf-8 -*-

from gi.repository import GObject as gobject, Gst as gst, Gtk as gtk, GdkX11, GstVideo
import platform
import logging
import os

log = logging.getLogger(__name__)


class Player(object):
    VIDEO = 0
    IMAGE = 1

    def __init__(self, window, url, cb_finish, cb_error, mode=VIDEO):
        self.window = window
        self.mode = mode
        self.url = url
        self.cb_finish = cb_finish
        self.cb_error = cb_error

        # The play binary pipeline
        self.pipeline = gst.ElementFactory.make("playbin", "player")
        self.pipeline.set_property("uri", url)

        # Sink
        if platform.system() == "Windows":
            self.sink = gst.ElementFactory.make('d3dvideosink', 'sink')
        else:
            self.sink = gst.ElementFactory.make('ximagesink', 'sink')
            self.sink.set_property('force-aspect-ratio', True)
        self.pipeline.set_property('video-sink', self.sink)

        # Handle image stuff
        if mode == Player.IMAGE:
            self.freeze = gst.ElementFactory.make("imagefreeze", "freeze")
            self.pipeline.add(self.freeze)
        else:
            self.freeze = None

        # Add signal handler
        self.bus = self.pipeline.get_bus()
        self.bus.connect('message::eos', self.handle_eos)
        self.bus.connect('message::error', self.handle_error)
        self.bus.add_signal_watch()

        # Find the correct window handle and set it as base drawing area for the video sink
        if platform.system() == "Windows":
            self.sink.set_window_handle(self.window.get_hwnd())
        else:
            self.sink.set_window_handle(self.window.get_xid())

        # Start
        self.pipeline.set_state(gst.State.PLAYING)

    def handle_error(self, bus, msg):
        error = msg.parse_error()[1]
        log.warn(u"Caught error {0}".format(error))
        self.cb_error(error)

    def handle_eos(self, bus, msg):
        log.info(u"End of stream")
        self.cb_finish()

    def play(self):
        self.pipeline.set_state(gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(gst.State.NULL)

    def pause(self):
        self.pipeline.set_state(gst.State.PAUSED)

    def is_stopped(self):
        return self.pipeline.get_state(gst.CLOCK_TIME_NONE)[1] == gst.State.NULL

    def is_playing(self):
        return self.pipeline.get_state(gst.CLOCK_TIME_NONE)[1] == gst.State.PLAYING

    def is_paused(self):
        return self.pipeline.get_state(gst.CLOCK_TIME_NONE)[1] == gst.State.PAUSED

    def close(self):
        self.stop()
        self.bus.remove_signal_watch()

    def status(self):
        if self.is_stopped():
            return 0
        if self.is_playing():
            return 1
        if self.is_paused():
            return 2
        return None

    def seek(self, seconds):
        self.pipeline.seek_simple(gst.Format.TIME,
                                  gst.SeekFlags.FLUSH | gst.SeekFlags.KEY_UNIT,
                                  seconds * gst.SECOND)
