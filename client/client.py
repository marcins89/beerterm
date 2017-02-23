'''
Created on 25.01.2017

@author: sosna
'''
import time
import sys
import os
import websocket as wbs

from tornado import websocket, ioloop, web, gen
from datetime import timedelta

dirname, filename = os.path.split(os.path.abspath(__file__))

tempfile = open(dirname + "/config")
serverIp = tempfile.read()
tempfile.close()

server_url = 'ws://' + serverIp + ':81/in'

cl = []
i = 0
public_path = dirname + '/../frontend/termometr/dist/'

class MainHandler(web.RequestHandler):
    def get(self):
        self.render(public_path + 'index.html')

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
        self.write_message(u"OK")

    def on_close(self):
        if self in cl:
            cl.remove(self)
        
    def on_message(self, message):
        self.write_message("OK!")

app = web.Application([
    (r'/', MainHandler),
    (r'/(.*)', web.StaticFileHandler, {'path': public_path})
])

app_socket = web.Application([
    (r'/', SocketHandler),
])

def send_message():
    global i
    global cl
    try:
        tempfile = open("/sys/bus/w1/devices/28-05167355eeff/w1_slave")
        text = tempfile.read()
        tempfile.close()
        tempdata = text.split("\n")[1].split(" ")[9]
        temp = float(tempdata[2:])
        temp = temp / 1000
        msg = "%.2f C \r" % (temp)
        sys.stdout.write(msg)
        for client in cl:
#             print("send");
            client.write_message(msg)
        ws.send(msg)
    finally:
        ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), send_message)
        
def initSocket():
    global ws
    ws = wbs.WebSocket()
    ws.connect(server_url)

if __name__ == '__main__':
    initSocket()
    app.listen(80)
    app_socket.listen(81)
    ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), send_message)
    ioloop.IOLoop.instance().start()
