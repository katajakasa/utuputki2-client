# -*- coding: utf-8 -*-

from gi.repository import GObject as gobject, Gst as gst, Gtk as gtk, GdkX11, GstVideo
import platform
import logging

log = logging.getLogger(__name__)


class Player(object):
    def __init__(self, window):
        self.fd = None
        self.window = window

        # The play binary pipeline
        self.pipeline = gst.ElementFactory.make("playbin2", None)

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
        return not self.pipeline.get_state(gst.State.PLAYING)

    def is_playing(self):
        return self.pipeline.get_state(gst.State.PLAYING)

    def is_paused(self):
        return self.pipeline.get_state(gst.State.PAUSED)

    def seek(self, seconds):
        self.pipeline.seek_simple(gst.Format.TIME,
                                  gst.SeekFlags.FLUSH | gst.SeekFlags.KEY_UNIT,
                                  seconds * gst.SECOND)
