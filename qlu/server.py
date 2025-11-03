#!/usr/bin/env python3

import socket

import cherrypy


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


class ServerContext:
    started = False

    def __enter__(self):
        port = cherrypy.config.get("server.socket_port")
        if is_port_in_use(port):
            return
        print(f"started on {port}")
        self.started = True
        cherrypy.engine.start()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.started:
            cherrypy.engine.exit()
