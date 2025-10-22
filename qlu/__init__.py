from qlu.engines.slob import SlobEngine
import cherrypy

engines = [SlobEngine()]

cherrypy.config.update(
    {
        "environment": "embedded",
        "server.socket_port": 8023,
    }
)

config = {"/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()}}

for engine in engines:
    cherrypy.tree.mount(engine.handler, engine.BASE, config=config)
