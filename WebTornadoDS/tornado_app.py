#*********************************************************************
# ESP8266ARS: Python project for WebTornadoDS
#
# Author(s): Daniel Roldan <droldan@cells.es>
#
# Copyright (C) 2017, CELLS / ALBA Synchrotron
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import json, os
import threading

import fandango as fn
import tornado
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler


class MainHandler(RequestHandler):
    def initialize(self, path):
        self.path= path


    def get(self, url=None):
        to_render = "index.html"
        if url != '':
            if not url.endswith('json') and not url.endswith('html'):
                if not url.endswith('/'):
                    self.redirect(url+'/')
                to_render = os.path.join(self.path, url, 'index.html')
            else:

                to_render = os.path.join(self.path, url)
        print "Rendering %s" % to_render

        self.render(to_render)

class TangoDSSocketHandler(WebSocketHandler):
    waiters = set()

    def initialize(self, parent):
        self._parent = parent

    def open(self):
        # Add client to list
        self.waiters.add(self)
        client = self.request.remote_ip
        print "Socket open with client " + str(client)
        print "Main data waiters list lenght %s" % len(self.waiters)
        self._parent.newClient(self)


    def on_close(self):
        # Remove client form clients list
        client = self.request.remote_ip
        self.waiters.remove(self)
        print "Socket closed client " + str(client)
        print "Main waiters list lenght %s" % len(self.waiters)

    def unicode2python(self, obj):
        if fn.isMapping(obj):
            n = dict(self.unicode2python(t) for t in obj.items())
        elif fn.isSequence(obj):
            n = list(self.unicode2python(t) for t in obj)
        elif fn.isString(obj):
            n = str(obj)
        else:
            n = obj
        return n

    def on_message(self, jsondata):
        # Process message form client
        client = self.request.remote_ip
        try:

            jsondata = json.loads(jsondata, object_hook=self.unicode2python)
            jsondata = dict(jsondata)

            # SaveNewConfig is called whn the Web page save or delete a new
            # config
            if 'SaveNewConfig' in jsondata.keys():
                conf = jsondata['SaveNewConfig']
                conf = json.dumps(conf)

                # Call to DS in order to save the config in the properties
                self._parent.setStructureConfig(conf)

            print "Client=", client, " DATA=", conf
        except Exception, e:
            response = "IP Client:" + client + " ERROR!!: Invalid Command!! " + str(
                e)
            print response


class TornadoManagement(object):
    
    def __init__(self, port=8888, parent=None,):
        self._webport = port


        path = os.path.dirname(os.path.abspath(__file__))
        try:
            webfilespath = self.parent.WebFilesPath
            if webfilespath != "":
                path = webfilespath
        except:
            pass


        self.template_path = path + "/templates"
        self.static_path = path + "/static"
        self.Json_static = path + "/JSONfiles/"

        self.handlers = [
                    #(r"/index.html", MainHandler),
                    (r"/service/*", TangoDSSocketHandler,
                     {"parent": parent}),
                    # (r"/*/(.*json*)", tornado.web.StaticFileHandler,
                    #  {'path': self.Json_static}),
                    (r"/(.*)", MainHandler,  {'path': self.Json_static}),]
        self.server = None
        self.started = False

    def start(self):
        # Starting Tornado async
        self.thread = threading.Thread(target=self._startTornado)
        self.thread.start()

    def _startTornado(self):
        application = Application(self.handlers,
                                   static_path=self.static_path,
                                   template_path=self.template_path,
                                   debug=True)
        # Created a simple gHHTPServer to manage the server
        # and close it on Stop, else the port is in use
        from tornado.httpserver import HTTPServer
        self.server = HTTPServer(application)
        self.server.listen(self._webport)

        self.started = True
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        # Close the HTPServer use the port
        self.server.stop()

        # stop the tornado Service
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_callback(ioloop.stop)

        self.thread.join()
        self.started = False

    def isRunning(self):
        return self.started


