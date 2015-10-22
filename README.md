# Utuputki2-client

Utuputki2-client is a really simple Python/GTK/GStreamer client for utuputki. Uses websockets to connect the server.

Installation
------------

1. Install requirements (to virtualenv)
2. Get API token from Utuputki2 server
3. Copy config.py-dist to config.py and modify to match your setup
4. Start client by running streamer.py.

Requirements
------------

To get dependencies for Windows, see PyGObjectWin32 project. On linux, use pip or your distributions own 
package repository.

* websocket-client (pip install websocket-client)
* PyGObject
* GTK+ 3
* GStreamer (codec support!)

License
-------

MIT. Please refer to LICENSE for more information.
