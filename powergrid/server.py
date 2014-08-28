import json
import os.path

from tornado.ioloop import IOLoop
from tornado.web import Application, url, RequestHandler
from tornado.websocket import WebSocketHandler

import game
import player


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
        elif msg['type'] == "COSTREQUEST":
            self.handle_costrequest(msg)
        elif msg['type'] == "PURCHASE":
            self.handle_purchase(msg)
        elif msg['type'] == "CLEARBOARD":
            self.handle_clearboard(msg)
        elif msg['type'] == "REQUESTCOLORS":
            self.handle_requestcolors(msg)
        elif msg['type'] == "CHANGECOLOR":
            self.handle_changecolor(msg)

    def handle_connect(self):
        # send current player info
        self.player.notify("YOURPLAYER", {'name': self.player.name,
                                          'color': self.player.color})

        self.player.notify("BOARDINFO", PlayerHandler.game.board.get_board_info())

        # send other player info
        for other in PlayerHandler.game.players:
            if other != self.player:
                self.player.notify("NEWPLAYER", {'name': other.name,
                                                 'color': other.color})


    def handle_costrequest(self, msg):
        cost, paths = self.game.board.get_cost(msg['body']['player'], msg['body']['cities'])
        self.player.notify("COSTRESULT", {'cost': cost})

    def handle_purchase(self, msg):
        cities = msg['body']['cities']
        result = {'purchased': [],
                  'error': ''}
        for city in cities:
            try:
                PlayerHandler.game.board.add_house(city, self.player)
                result['purchased'].append(city)
            except:
                result['error'] = 'failed to purchase house'

        self.player.notify("PURCHASERESULT", result)
        # notify all players of new board state
        board_info = PlayerHandler.game.board.get_board_info()
        for p in PlayerHandler.game.players:
            p.notify("BOARDINFO", board_info)

    def handle_clearboard(self, msg):
        self.game.board.clear_board()
        board_info = PlayerHandler.game.board.get_board_info()
        for p in PlayerHandler.game.players:
            p.notify("BOARDINFO", board_info)

    def handle_requestcolors(self, msg):
        available = list(player.PLAYER_COLORS)
        self.player.notify("COLORSAVAILABLE", available)

    def handle_changecolor(self, msg):
        color = msg['body'][0]
        self.player.change_color(color)
        for other in PlayerHandler.game.players:
            if other != self.player:
                other.notify("DEADPLAYER", self.player.name)
                other.notify("NEWPLAYER", self.player.name)
        self.player.notify("YOURPLAYER", {"name": self.player.name,
                                          "color": self.player.color})

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
