import json

PLAYER_IDS = set(zip(range(6), ['red', 'yellow', 'green', 'blue', 'black', 'purple']))


class Player(object):
    def __init__(self, playerhandler):
        if not PLAYER_IDS:
            raise ValueError("too many players")
        self.id, self.color = PLAYER_IDS.pop()
        self.name = "player " + str(self.id)
        self.handler = playerhandler

    def notify(self, msg_type, body):
        self.handler.write_message(json.dumps({'type': msg_type,
                                               'body': body}))

    def destroy(self):
        PLAYER_IDS.add((self.id, self.color))
