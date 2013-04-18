import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.framing import Frame, OPCODE_BINARY
from ws4py.messaging import TextMessage, BinaryMessage
import numpy as N

cherrypy.config.update({'server.socket_port': 9002})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

SUBSCRIBERS = set()

class Publisher(WebSocket):
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        SUBSCRIBERS.add(self)

    def received_message(self, m):
        # Assuming type of arraybuffer
        xx = N.fromstring(m.data, N.int16, count=5)
        # xx = N.fromstring(m.data, N.float32, count=4)
        print xx
        xx = xx*2;
        f = Frame(OPCODE_BINARY, xx.tostring(), fin=1)
        b = f.build()
        yy = BinaryMessage(b)
        for conn in SUBSCRIBERS:
        	conn.send(yy)

    def closed(self, code, reason=None):
        SUBSCRIBERS.remove(self)

class Root(object):
    @cherrypy.expose
    def index(self):
        return open('ws_browser.html').read()

    @cherrypy.expose
    def ws(self):
        "Method must exist to serve as a exposed hook for the websocket"

    @cherrypy.expose
    def notify(self, msg):
        for conn in SUBSCRIBERS:
            conn.send(msg)

cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True,
                                                 'tools.websocket.handler_cls': Publisher}})
