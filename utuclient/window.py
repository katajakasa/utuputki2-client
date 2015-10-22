# -*- coding: utf-8 -*-

from gi.repository import Gtk as gtk, GdkX11, GstVideo, Gdk
import ctypes
import logging

log = logging.getLogger(__name__)


class Window(object):
    def __init__(self):
        # Gtk window
        self.window = gtk.Window()
        self.window.connect('destroy', self.on_window_destroy)
        self.window.set_title("Utuputki")
        self.window.fullscreen()

        # Drawing area
        self.area = gtk.DrawingArea()
        self.window.add(self.area)

        self.window.show_all()
        self.open = True

    def get_xid(self):
        return self.area.get_property('window').get_xid()

    def run(self):
        gtk.main()

    def get_hwnd(self):
        # http://stackoverflow.com/questions/23021327/how-i-can-get-drawingarea-window-handle-in-gtk3
        Gdk.threads_enter()
        drawingareawnd = self.area.get_property("window")
        ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
        ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object]
        drawingarea_gpointer = ctypes.pythonapi.PyCapsule_GetPointer(drawingareawnd.__gpointer__, None)
        gdkdll = ctypes.CDLL("libgdk-3-0.dll")
        hnd = gdkdll.gdk_win32_window_get_handle(drawingarea_gpointer)
        Gdk.threads_leave()
        return hnd

    def close(self):
        if self.open:
            self.window.close()
            self.window.destroy()
            self.open = False

    def is_open(self):
        return self.open

    def on_window_destroy(self, nx):
        gtk.main_quit()

