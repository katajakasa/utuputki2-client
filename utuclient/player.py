# -*- coding: utf-8 -*-

from gi.repository import GObject as gobject, Gst as gst, Gtk as gtk, GdkX11, GstVideo
import platform
import logging

log = logging.getLogger(__name__)


class Player(object):
    def __init__(self, window, cb_finish):
        self.fd = None
        self.window = window

        # The play binary pipeline
        self.pipeline = gst.ElementFactory.make("playbin", "player")
        self.pipeline.connect("about-to-finish", cb_finish)

        # Sink
        if platform.system() == "Windows":
            self.sink = gst.ElementFactory.make('d3dvideosink', 'sink')
        else:
            self.sink = gst.ElementFactory.make('xvimagesink', 'sink')
            self.sink.set_property('force-aspect-ratio', True)
        self.pipeline.set_property('video-sink', self.sink)

        # Find the correct window handle and set it as base drawing area for the video sink
        if platform.system() == "Windows":
            self.sink.set_window_handle(self.window.get_hwnd())
        else:
            self.sink.set_window_handle(self.window.get_xid())

    def set_src(self, address):
        self.pipeline.set_property("uri", address)

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
