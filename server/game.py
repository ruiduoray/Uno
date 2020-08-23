"""
game.py
This file handles the game logic for the server
Ray Gong, ruiduoray@berkeley.edu, 8/22/2020
"""
from cards import *
from player import *

class Game:
	def __init__(self, user_list):
		self.deck = Deck()
		self.player_list = [Player(user_list[i], i) for i in range(len(user_list))]
		for player in self.player_list:
			for _ in range(7):
				self.deal_card_to_player(player)

		self.player_amount = len(self.player_list)
		self.direction = 1
		self.top_card = self.deck.draw_card()
		self.current_player_index = 0
		self.game_end = False
		self.rank_list = []

	def play(self, player, color, symbol, wild_color = None):
		if player is not self.current_player():
			raise Exception("Not current player")
		if not player.in_hand(color, symbol):
			raise Exception("Card not in hand")
		card = player.get_card(color, symbol)	
		if not card.playable(self.top_card):
			raise Exception("Card not playable")
		if color in WILD_LIST and wild_color is None:
			raise Exception("No color for wild card")

		self.top_card = player.play_card(color, symbol)
		card = self.top_card

		if color == "Wild":
			card.color = wild_color
		if card.symbol == "R":
			self.direction *= -1
		elif card.symbol == "S":
			self.current_player_index = self.next_player_index()
		elif card.symbol == "D":
			for _ in range(2):
				self.deal_card_to_player(self.next_player())
		elif card.symbol == "D4":
			for _ in range(4):
				self.deal_card_to_player(self.next_player())
		player.drew = False
		if not player.still_in_game():
			self.rank_list.append(player.user.username)
		self.current_player_index = self.next_player_index()
		self.check_end_game()
		if self.game_end:
			for player in self.player_list:
				if player.still_in_game():
					self.rank_list.append(player.user.username)

	def draw(self, player):
		if player is not self.current_player():
			raise Exception("Not current player")
		if player.drew:
			raise Exception("Player already drew a card this round")
		self.deal_card_to_player(player)
		player.drew = True

	def skip(self, player):
		if player is not self.current_player():
			raise Exception("Not current player")
		if not player.drew:
			raise Exception("Player haven't drew a card yet")
		self.current_player_index = self.next_player_index()
		player.drew = False

	def deal_card_to_player(self, player):
		player.add_card(self.deck.draw_card())

	def next_player_index(self):
		ret = (self.current_player_index + self.direction) % self.player_amount
		while not self.player_list[ret].still_in_game():
			ret = (ret + self.direction) % self.player_amount
		return ret

	def current_player(self):
		return self.player_list[self.current_player_index]

	def next_player(self):
		return self.player_list[self.next_player_index()]

	def check_end_game(self):
		self.game_end = len([1 for player in self.player_list if player.still_in_game()]) <= 1