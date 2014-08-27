import json
import os.path

from tornado.ioloop import IOLoop
from tornado.web import Application, url, RequestHandler
from tornado.websocket import WebSocketHandler

from . import game
from . import player


HERE = os.path.dirname(__file__)


class PlayerHandler(WebSocketHandler):
    game = game.Game("america")

    def open(self):
        try:
            # noinspection PyAttributeOutsideInit
            self.player = player.Player(self)
        except ValueError:
            self.close(reason='too many players')

        PlayerHandler.game.add_player(self.player)

    def on_message(self, msg):
        msg = json.loads(msg)
        if msg['type'] == "CONNECT":
            self.handle_connect()

    def handle_connect(self):
        # send current player info
        self.player.notify("YOURPLAYER", {'name': self.player.name,
                                          'color': self.player.color})
        # send other player info
        for other in PlayerHandler.game.players:
            if other != self.player:
                self.player.notify("NEWPLAYER", {'name': other.name,
                                                 'color': other.color})

    def on_close(self):
        self.player.destroy()
        PlayerHandler.game.remove_player(self.player)


class MainHandler(RequestHandler):
    def get(self):
        return self.render("static/html/index.html")


def make_app():
    settings = {'debug': True,
                'static_path': os.path.join(HERE, "./static/")}
    return Application([url(r"/", MainHandler),
                        url(r"/ws", PlayerHandler)], **settings)


def main():
    app = make_app()
    app.listen(address="0.0.0.0", port=8080)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
