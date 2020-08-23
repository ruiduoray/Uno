"""
player.py
This file handles the logic of players in the game
Ray Gong, ruiduoray@berkeley.edu, 8/22/2020
"""
COLOR_DICT = {1: "Red", 2: "Yellow", 3: "Blue", 4: "Green"}

class Player:
	def __init__(self, user, index):
		user.player = self
		self.hands = []
		self.index = index
		self.user = user
		self.drew = False

	def still_in_game(self):
		return len(self.hands) > 0

	def add_card(self, card):
		self.hands.append(card)

	def pop_card(self, index):
		return self.hands.pop(index)

	def in_hand(self, color, symbol):
		for card in self.hands:
			if color == card.color and symbol == card.symbol:
				return True
		return False

	def get_card(self, color, symbol):
		for card in self.hands:
			if color == card.color and symbol == card.symbol:
				return card

	def play_card(self, color, symbol):
		for card in self.hands:
			if color == card.color and symbol == card.symbol:
				self.hands.remove(card)
				return card