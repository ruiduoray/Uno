"""
cards.py
This file handles the logic of the cards.
This file should be synchronized for both client and server
A deck contains:
Red,Yellow,Blue,Green
0,1-9(x2), Reverse(x2), Skip(x2), Draw(x2)
and
Wild
Wild(x4), Draw4(x4)
Ray Gong, ruiduoray@berkeley.edu, 8/22/2020
"""
from random import shuffle


COLOR_LIST = ["Red", "Yellow", "Blue", "Green"]
SYMBOL_LIST = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "R", "S", "D"]
WILD_LIST = ["Wild"]
WILD_SYMBOL_LIST = ["W", "D4"]
SORT_WEIGHT = {"Wild": 0, "Red": 1, "Yellow": 2, "Blue": 3, "Green": 4,
"0": 12, "1": 11, "2": 10, "3": 9, "4": 8, "5": 7, "6": 6, "7": 5, "8": 4, "9": 3, "R": 2, "S": 1, "D": 0,
"W": 1, "D4": 0}


class Card:
	def __init__(self, color, symbol):
		self.color = color
		self.symbol = symbol

	def playable(self, prev_card):
		if self.color == "Wild" or prev_card.color == 'Wild':
			return True
		if self.color == prev_card.color or self.symbol == prev_card.symbol:
			return True
		return False

	def __str__(self):
		return self.color + " " + self.symbol

	def __repr__(self):
		return self.__str__()


class Deck:
	def __init__(self):
		self._deck = []
		for color in COLOR_LIST:
			for symbol in SYMBOL_LIST:
				if symbol == "0":
					amount = 1
				else:
					amount = 2
				for _ in range(amount):
					self._deck.append(Card(color, symbol))
		for color in WILD_LIST:
			for symbol in WILD_SYMBOL_LIST:
				for _ in range(4):
					self._deck.append(Card(color,symbol))
		shuffle(self._deck)

	def draw_card(self):
		return self._deck.pop()

	def is_deck_empty(self):
		return len(self._deck) > 0

	def cards_left(self):
		return len(self._deck)


#Only for testing purpose
class WildDeck(Deck):
	def __init__(self):
		self._deck = []
		for _ in range(108):
			self._deck.append(Card("Wild", "W"))


def sort_card_list(card_list):
	card_list.sort(key = lambda card: SORT_WEIGHT[card.color] * 15 + SORT_WEIGHT[card.symbol])

def sort_str_card_list(str_list):
	ret = list(str_list)
	ret.sort(key = lambda card: SORT_WEIGHT[card[0]] * 15 + SORT_WEIGHT[card[1]])
	return ret