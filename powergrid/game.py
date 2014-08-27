from . import board

import os.path

HERE = os.path.dirname(__file__)

class Game(object):
	def __init__(self, board_name):
		self.players = []
		self.load_board(board_name)

	def add_player(self, newplayer):
		self.players.append(newplayer)
		# broadcast
		for player in self.players:
			if player != newplayer:
				player.notify("NEWPLAYER", {'name': newplayer.name,
											'color': newplayer.color})

	def remove_player(self, oldplayer):
		self.players.remove(oldplayer)
		for player in self.players:
			player.notify("DEADPLAYER", {'name': oldplayer.name,
										 'color': oldplayer.color})
		

	def load_board(self, board_name):
		board_path = os.path.join(HERE, "./boards/{}.json".format(board_name))
		self.board = board.Board(board_path)
