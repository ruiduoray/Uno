"""
client.py
This file handles the backend code of the client.
Ray Gong, ruiduoray@berkeley.edu, 8/22/2020
"""

import json
from requests import post, get


#Local URL is used when server is running on local
LOCAL_URL = 'http://127.0.0.1:5000/api/'
SERVER_URL = 'This should be the actual server url'
TIMEOUT = 1
#Set LOCAL to True to use LOCAL_URL and set to False to use SERVER_URL when sending requests
LOCAL = True

class Client:
    def __init__(self):
        self.test_connection()

    def test_connection(self):
        try:
            return self.__get_request__('test_connection')
        except Exception as e:
            raise ServerDownException("Server Down")

    def create_username(self, username):
        status_code, response =  self.__post_request__('create_username', {'username': username})
        if status_code == 200:
            self.username = username
        return status_code, response

    def change_username(self, new_username):
        status_code, response = self.__post_request__('change_username', {'new_username':new_username})
        if status_code == 200:
            self.username = username
        return status_code, response

    def create_room(self):
        return self.__post_request__('create_room')

    def join_room(self, room_number):
        return self.__post_request__('join_room', {'room_number': room_number})

    def quit_room(self):
        return self.__post_request__('quit_room')

    def send_exit_signal(self):
        self.__post_request__('exit_signal')

    def get_lobby_info(self):
        return self.__get_request__('lobby_info')

    def get_room_info(self):
        return self.__post_request__('room_info')

    def start_game(self):
        return self.__post_request__('start_game')

    def user_ready(self):
        return self.__post_request__('user_ready')

    def get_game_meta_data(self):
        return self.__post_request__('game_meta_data')

    def get_game_info(self):
        return self.__post_request__('game_info')

    def play_card(self, color, symbol, wild_color = None):
        return self.__post_request__('play_card', {'color': color, 'symbol': symbol, 'wild_color': wild_color})

    def draw_card(self):
        return self.__post_request__('draw_card')

    def skip_card(self):
        return self.__post_request__('skip_card')

    def __get_request__(self, endpoint):
        url = LOCAL_URL + endpoint
        response = get(url)
        return response.status_code, response.json()

    def __post_request__(self, endpoint, data = None):
        if not data:
            data = {}
        if 'username' not in data:
            data['username'] = self.username
        url = LOCAL_URL + endpoint if LOCAL else SERVER_URL + endpoint
        response = post(url, data=data, timeout=TIMEOUT)
        return response.status_code, response.json()


class ServerDownException(Exception):
    def __init__(self, msg):
        self.msg = msg