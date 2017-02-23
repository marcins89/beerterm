'''
Created on 25.01.2017

@author: sosna
'''
import time
import sys
import os

from tornado import websocket, ioloop, web, gen
from datetime import timedelta

dirname, filename = os.path.split(os.path.abspath(__file__))

cl_out = []
cl_in = []
i = 0;
public_path = dirname + '/../frontend/termometr/dist/'

class MainHandler(web.RequestHandler):
    def get(self):
        self.render(public_path + 'index.html')

class OutSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
	print self
        if self not in cl_out:
            cl_out.append(self)
        self.write_message(u"OK")

    def on_close(self):
        if self in cl_out:
            cl_out.remove(self)
        
    def on_message(self, message):
        self.write_message("OK!")
        
class InSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
	print self
        if self not in cl_in:
            cl_in.append(self)
        self.write_message(u"OK")

    def on_close(self):
        if self in cl_in:
            cl_in.remove(self)
        
    def on_message(self, message):
	print message
        for client in cl_out:
            client.write_message(message)
        self.write_message("OK!")

app = web.Application([
    (r'/', MainHandler),
    (r'/(.*)', web.StaticFileHandler, {'path': public_path})
])

app_socket = web.Application([
    (r'/', OutSocketHandler),
    (r'/in', InSocketHandler)
])

if __name__ == '__main__':
    app.listen(80)
    app_socket.listen(81)
    ioloop.IOLoop.instance().start()
