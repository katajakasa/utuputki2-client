# -*- coding: utf-8 -*-

import gi
from gi.repository import GObject as gobject, Gst as gst, GLib as glib
from controller import Controller

# Attempt to find configuration
try:
    import config
except ImportError:
    print "Config module not found! Make sure config.py exists!"
    exit(1)


if __name__ == "__main__":
    gi.require_version("Gst", "1.0")
    glib.threads_init()
    gobject.threads_init()
    gst.init(None)

    c = Controller(config.UTUPUTKI_API_URL,
                   config.UTUPUTKI_API_TOKEN,
                   config.UTUPUTKI_VIDEO_URL)
    try:
        c.run()
    except KeyboardInterrupt:
        c.close()

    exit(0)
