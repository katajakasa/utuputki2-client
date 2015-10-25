# Utuputki2-client

Utuputki2-client is a really simple Python/GTK/GStreamer client for utuputki. It uses websockets to connect the server.

## Installation

1. Install requirements (see below)
2. Get API token from Utuputki2 server
3. Copy config.py-dist to config.py and modify to match your setup. Remember to set correct URL for server, and make
   sure the access token is set (You can get this via the tools module in Utuputki2 server!).
4. Start client `python -m utuclient.main`

## Requirements

* websocket-client (pip install websocket-client)
* PyGObject
* GTK+ 3
* GStreamer (codec support!)

### Debian

Make sure you have ALL the plugins installed! You may need to add restricted repositoried or such to get everything.

```
apt-get install python-gi gir1.2-gstreamer-1.0 gir1.2-gtk-3.0 gir1.2-glib-2.0 \
        gir1.2-gst-plugins-base-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly python-websocket
```

### Windows

To get dependencies for Windows, see [PyGObjectWin32](http://sourceforge.net/projects/pygobjectwin32/) project. 
Make sure that at least gobject, gstreamer, gtk3 and gstreamer plugins packages are selected for installation.
In addition, python-websocket needs to be installed, for example via pip.

## License

MIT. Please refer to LICENSE for more information.
