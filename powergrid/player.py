import json

PLAYER_COLORS = set(['red', 'yellow', 'green', 'blue', 'black', 'purple'])


class Player(object):
    def __init__(self, playerhandler):
        if not PLAYER_COLORS:
            raise ValueError("too many players")
        self.color = PLAYER_COLORS.pop()
        self.name = self.color + " player"
        self.handler = playerhandler

    def notify(self, msg_type, body):
        self.handler.write_message(json.dumps({'type': msg_type,
                                               'body': body}))

    def change_color(self, new_color):
        PLAYER_COLORS.add(self.color)
        PLAYER_COLORS.remove(new_color)
        self.color = new_color
        self.name = self.color + " player"

    def destroy(self):
        PLAYER_COLORS.add(self.color)
