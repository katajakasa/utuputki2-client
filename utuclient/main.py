# -*- coding: utf-8 -*-

import gi
gi.require_version("Gst", "1.0")
import logging
import sys
import signal
from gi.repository import GObject as gobject, Gst as gst, GLib as glib, Gtk as gtk

from controller import Controller

# Attempt to find configuration
try:
    import config
except ImportError:
    print "Config module not found! Make sure config.py exists!"
    exit(1)


if __name__ == "__main__":
    # Init GTK stuff
    glib.threads_init()
    gobject.threads_init()
    gst.init(None)

    # Set up the global log
    log_format = '[%(asctime)s] %(message)s'
    log_datefmt = '%d.%m.%Y %I:%M:%S'
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format=log_format,
                        datefmt=log_datefmt)
    log = logging.getLogger(__name__)

    # Our own stuff
    log.info(u"Starting up.")
    c = Controller(config.UTUPUTKI_API_URL,
                   config.UTUPUTKI_API_TOKEN,
                   config.FULLSCREEN)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    c.run()
    c.close()

    log.info(u"All done.")
    exit(0)
