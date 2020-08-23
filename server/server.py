"""
server.py
The server of the game.
To start the serve on local, run command 'python3 server.py'
To start the server on public, add argument 'host = 0.0.0.0' at the last line in app.run(), then run the same command above
There should be more settings to change in your environment such as firewall if you want to serve this as a real server
Ray Gong, ruiduoray@berkeley.edu, 8/22/2020
"""
from flask import Flask, jsonify, request
import json
from game import *

app = Flask(__name__)
USERNAME_SET = set()
USER_DICT = {}
ROOM_DICT = {}

@app.route('/api/test_connection', methods=['GET'])
def test_connection():
	return jsonify({"error": None})

@app.route('/api/create_username', methods=['POST'])
def create_username():
	if 'username' not in request.form:
		return jsonify({"error": "No username in the request"}), 400
	username = str(request.form['username'])
	if username in USERNAME_SET:
		return jsonify({"error": "Username is already taken"}), 403
	elif len(username) < 3:
		return jsonify({"error": "Username has to contain at least three characters"}), 403
	else:
		User(username)
		return jsonify({'error': None})

@app.route('/api/change_username', methods=['POST'])
def change_username():
	if 'username' not in request.form:
		return jsonify({"error":"No username in the request"}), 400
	username = str(request.form['username'])
	if username in USERNAME_SET:
		return jsonify({"error":"Username is already taken"}), 403
	elif len(username) < 3:
		return jsonify({"error": "Username has to contain at least three characters"}), 403
	else:
		USER_DICT[username].change_username(username)
		return jsonify({'error': None})

@app.route('/api/create_room', methods=['POST'])
def create_room():
	if 'username' not in request.form:
		return jsonify({"error":"No username in the request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		room = Room(user.username)
		user.room = room
		return jsonify({'room_number': room.room_number, 'hostname': room.hostname, 'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/lobby_info', methods = ['GET'])
def lobby_info():
	rooms = {}
	for room in ROOM_DICT.values():
		rooms[room.room_number] = {'user_number': len(room.userlist), 'hostname': room.hostname, 'inGame': room.inGame}
	return jsonify(rooms)

@app.route('/api/join_room', methods = ['POST'])
def join_room():
	if 'username' not in request.form or 'room_number' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		room = ROOM_DICT[int(request.form['room_number'])]
		if room.inGame:
			return jsonify({'error': "Game already started"}), 400
		user.join_room(room)
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/quit_room', methods = ['POST'])
def quit_room():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		user.quit_room()
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

"""
Room Info Return Type:
{'room_number': int value of the room number
'user_number': int value of number of players in room
'hostname': str name of the host player
'inGame': boolean value shows if the game started
'user_info': dict of the user infos
	{
	'0': (str name of the user at index 0, boolean value shows if ready)
	'1': (str name of the user at index 1, boolean value shows if ready)
	}
}
"""
@app.route('/api/room_info', methods = ['POST'])
def room_info():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		room = USER_DICT[str(request.form['username'])].room
		return jsonify(room.room_info)
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/start_game', methods = ['POST'])
def start_game():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		if user is not user.room.hostuser:
			return jsonify({'error': 'You are not the host. Cannot start the game!'}), 400
		elif len(user.room.userlist) < 2:
			return jsonify({'error': 'Need at least 2 players to start the game!'}), 400
		elif not all([u.ready or u is user.room.hostuser for u in user.room.userlist]):
			return jsonify({'error': 'Player not ready!'}), 400
		else:
			user.room.start_game()
			return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/user_ready', methods = ['POST'])
def user_ready():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		user.ready = not user.ready
		user.room.refresh_user_info()
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

"""
Game Info Return Type:
{'game_end': Boolean value indicate if the game ends
'current_player': current player's username
'next_player': next player's username
'top_card': tuple(card color, card symbol)
'cards': list of the cards the user has. [tuple(card color, card symbol), tuple(card color, card symbol)...]
'player_colors': list of str of colors for all players
'player_card_nums': list of int of cards left for all players
}
"""
@app.route('/api/game_info', methods = ['POST'])
def game_info():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		room = user.room
		if not room.inGame and room.game is None:
			return jsonify({'error': 'Game not yet started'}), 400
		else:
			room.game_info['cards'] = [(card.color, card.symbol) for card in user.player.hands]
			return jsonify(room.game_info)		
	except Exception as e:
		return jsonify({'error': str(e)}), 400

"""
Meta Data Return Type:
{'player_num': int of total players in the room
'index': int of the requested user's index
'0': Username at index 0
'1': Username at index 1
...
}
"""
@app.route('/api/game_meta_data', methods = ['POST'])
def game_meta_data():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		ret_data = {}
		player_list = user.room.game.player_list
		for i in range(len(player_list)):
			ret_data[str(i)] = (player_list[i].user.username)
		ret_data['player_num'] = len(player_list)
		ret_data['index'] = user.player.index
		return jsonify(ret_data)
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/play_card', methods = ['POST'])
def play_card():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		if 'wild_color' in request.form:
			wild_color = str(request.form['wild_color'])
		else:
			wild_color = None
		user.room.play_card(user, str(request.form['color']), str(request.form['symbol']), wild_color)
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/draw_card', methods = ['POST'])
def draw_card():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		user.room.draw_card(user)
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/api/skip_card', methods = ['POST'])
def skip_card():
	if 'username' not in request.form:
		return jsonify({"error":"Bad request"}), 400
	try:
		user = USER_DICT[str(request.form['username'])]
		user.room.skip_card(user)
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400


@app.route('/api/exit_signal', methods=['POST'])
def exit_signal():
	if 'username' not in request.form:
		return jsonify({"error":"No username in the request"}), 400
	try:
		USER_DICT[str(request.form['username'])].clean_up()
		return jsonify({'error': None})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

	
class Room:
	ROOM_NUMBER_LIST = [i for i in range(0,100)]
	MAX_PLAYER = 10
	def __init__(self, hostname):
		if len(self.ROOM_NUMBER_LIST) == 0:
			raise Exception("Full Capacity")
		self.room_number = min(self.ROOM_NUMBER_LIST)
		self.ROOM_NUMBER_LIST.remove(self.room_number)
		ROOM_DICT[self.room_number] = self
		self.hostname = hostname
		self.hostuser = USER_DICT[hostname]
		self.userlist = [self.hostuser]
		self.inGame = False
		self.room_info = {'room_number': self.room_number, 'user_number': len(self.userlist), 'hostname': self.hostname,
				'inGame': self.inGame, 'user_info': {}}
		self.refresh_user_info()
		self.game_info = None

	def refresh_user_info(self):
		self.room_info['user_info'] = {}
		for i in range(len(self.userlist)):
			self.room_info['user_info'][str(i)] = (self.userlist[i].username, self.userlist[i].ready)

	def join_user(self, user):
		if len(self.userlist) >= 10:
			raise Exception("Full Room")
		self.userlist.append(user)
		self.refresh_user_info()
		self.room_info['user_number'] += 1

	def quit_user(self, user):
		self.userlist.remove(user)
		self.refresh_user_info()
		self.room_info['user_number'] -= 1
		if self.hostuser is user:
			if len(self.userlist) > 0:
				self.hostuser = self.userlist[0]
				self.hostname = self.hostuser.username
				self.room_info['hostname'] = self.hostname
			else:
				self.clean_up()

	def clean_up(self):
		self.ROOM_NUMBER_LIST.append(self.room_number)
		ROOM_DICT.pop(self.room_number)

	def start_game(self):
		self.game = Game(self.userlist)
		self.game_info = {'game_end': self.game.game_end, 'current_player': self.game.current_player().user.username, 
		'next_player': self.game.next_player().user.username,'top_card': (self.game.top_card.color, self.game.top_card.symbol),
		'cards': [], 'player_colors': [], 'player_card_nums': []}
		self.update_color_and_card_num()
		self.inGame = True
		self.room_info['inGame'] = True

	def update_color_and_card_num(self):
		self.game_info['player_colors'] = []
		self.game_info['player_card_nums'] = []
		for player in self.game.player_list:
			if len(player.hands) <= 0:
				self.game_info['player_colors'].append('grey')
			elif self.game.current_player() is player:
				self.game_info['player_colors'].append('green')
			elif self.game.next_player() is player:
				self.game_info['player_colors'].append('yellow')
			else:
				self.game_info['player_colors'].append('white')
			self.game_info['player_card_nums'].append(len(player.hands))

	def play_card(self, user, color, symbol, wild_color = None):
		self.game.play(user.player, color, symbol, wild_color)
		self.game_info['top_card'] = (self.game.top_card.color, self.game.top_card.symbol)
		self.update_color_and_card_num()
		if self.game.game_end:
			self.game_info['game_end'] = True
			self.game_info['result'] = "\n".join([str(i + 1) + '. ' + self.game.rank_list[i] for i in range(len(self.game.rank_list))])
			for user in self.userlist:
				user.ready = False
			self.refresh_user_info()
			self.inGame = False
			self.room_info['inGame'] = False

	def draw_card(self, user):
		self.game.draw(user.player)
		self.update_color_and_card_num()

	def skip_card(self, user):
		self.game.skip(user.player)
		self.update_color_and_card_num()


class User:
	def __init__(self, username):
		self.username = username
		self.room = None
		USER_DICT[username] = self
		USERNAME_SET.add(username)
		self.ready = False
		self.player = None
		self.index = None

	def change_username(self, new_username):
		self.clean_up()
		USER_DICT[new_username] = self
		USERNAME_SET.add(new_username)

	def join_room(self, room):
		room.join_user(self)
		self.room = room
		self.ready = False

	def quit_room(self):
		self.room.quit_user(self)
		self.room = None


	def clean_up(self):
		USER_DICT.pop(self.username)
		USERNAME_SET.remove(self.username)
		if self.room is not None:
			self.room.quit_user(self)

	def __str__(self):
		return self.username

	def __repr__(self):
		return self.__str__()



if __name__ == '__main__':
    app.run()