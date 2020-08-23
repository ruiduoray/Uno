"""
clientGUI.py
This file builds the GUI of the Cleint.
Images are imported from Yujie Qiu, yujieqiu55@gmail.com
To run the GUI use command 'python3 clientGUI.py'
Ray Gong, ruiduoray@berkeley.edu, 8/22/2020
"""
from client import *
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from cards import *
import atexit
from time import localtime, strftime


IMAGE_DICT = {}
COLOR = {'white': '#FFFFFF', 'grey': '#B2B3A5', 'yellow': '#DCEC1B', 'green': '#20FA20'} 


def log_with_timestamp(msg):
    print(strftime("%H:%M:%S", localtime()), msg)


class ClientGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("UNO")
        self.root.geometry("+600+200")
        self.root.minsize(500,500)
        self.next_page = self.create_username_page
        self.client = None
        try:
            self.client = Client()
            self.create_username_page()
            log_with_timestamp("Client Initialized")
            for color in COLOR_LIST:
                for symbol in SYMBOL_LIST:
                    IMAGE_DICT[color+symbol] = Image.open('Images/'+ color + symbol +'.png')
                for symbol in WILD_SYMBOL_LIST:
                    IMAGE_DICT[color+symbol] = Image.open('Images/'+ color + symbol +'.png')
            for color in WILD_LIST:
                for symbol in WILD_SYMBOL_LIST:
                    IMAGE_DICT[color+symbol] = Image.open('Images/'+ color + symbol +'.png')
            for color in COLOR_LIST:
                IMAGE_DICT[color] = Image.open('Images/' + color + '.png')
            log_with_timestamp("Images Loaded")
        except ServerDownException:
            log_with_timestamp("Server not available")
            self.server_down_page()       
        self.root.mainloop()


    def create_username_page(self):
        def create():
            username = username_entry.get()
            username_entry.delete(0, END)
            status_code, response = self.client.create_username(username)
            if status_code == 200:
                frame.destroy()
                self.root.after(30, self.lobby_page)
                return
            else:
                ErrorText.config(text = str(status_code) + ": " + response['error'])

        frame = Frame(self.root)
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        Label(frame, text = "Enter your username:", font = ("Times", 18)).place(relx = 0.25, rely = 0.25, relwidth = 0.5, relheight = 0.25)
        username_entry = Entry(frame)
        username_entry.place(relx = 0.25, rely = 0.5, relwidth = 0.3, relheight = 0.1)
        Button(frame, text = "Submit", font = ("Times", 18), command = create).place(relx = 0.55, rely = 0.5, relwidth = 0.2, relheight = 0.1)
        ErrorText = Message(frame)
        ErrorText.place(relx = 0.25, rely = 0.7, relwidth = 0.5, relheight = 0.2)


    def lobby_page(self):
        ROWVIEW = 2 #How many rooms to display in one row
        COLVIEW = 2 #How many rooms to display in one column
        ROOMVIEW = ROWVIEW * COLVIEW
        ROWOFFSET = 0.8 / ROWVIEW
        COLOFFSET = 0.8 / COLVIEW
        frame = Frame(self.root)
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        data, prev_data = None, None
        page_index = 1

        def create_room():
            status_code, response = self.client.create_room()
            if status_code != 200:
                frame.destroy()
                self.Error_page(status_code, response)
            else:
                frame.destroy()
                self.root.after(30, self.room_page)
                return

        def refresh():
            nonlocal data, prev_data
            status_code, data = self.client.get_lobby_info()
            log_with_timestamp('Refreshed Lobby')
            if status_code != 200:
                frame.destroy()
                self.Error_page(status_code, data)
            else:
                if data != prev_data:
                    set_up_page()
                else:
                    frame.after(1000, refresh)
                prev_data = data

        def set_up_page():
            log_with_timestamp("Setting up lobby!")
            nonlocal frame, page_index
            frame.destroy()
            frame = Frame(self.root)
            frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

            create_button = Button(frame, text = "Create Room",command = create_room)
            create_button.place(relx = 0.7, rely = 0.05, relwidth = 0.2, relheight = 0.05)

            room_numbers = list(data.keys())
            room_numbers.sort()

            if len(room_numbers) == 0:
                Label(frame, text = 'No room in the lobby. \nPress "Create Room" to create').place(relx = 0.1, rely = 0.1, relwidth = 0.8, relheight = 0.8)
            else:
                def click_back():
                    nonlocal page_index
                    if page_index > 1:
                        page_index -= 1
                        set_up_page()

                def click_next():
                    nonlocal page_index
                    if page_index <= len(room_numbers) // ROOMVIEW:
                        page_index += 1
                        set_up_page()

                slice_room_numbers = room_numbers[ROOMVIEW * (page_index - 1) : ROOMVIEW * page_index]
                counter = 0
                for room_number in slice_room_numbers:
                    col = counter // ROWVIEW
                    row = counter % ROWVIEW

                    def join_click(room_number = room_number):
                        status_code, response = self.client.join_room(room_number)
                        if status_code != 200:
                            frame.destroy()
                            self.Error_page(status_code, response)
                        else:
                            frame.destroy()
                            self.root.after(30, self.room_page)
                            return

                    room_info = data[room_number]
                    status = 'In Game' if room_info['inGame'] else 'Waiting'
                    room_label = Label(frame, borderwidth=2, relief="groove", text = 'user: ' + str(room_info['user_number']) + '/10\nhostname: ' + str(room_info['hostname'] + '\nstatus: ' + status))
                    room_label.place(relx = 0.1 + row * ROWOFFSET, rely = 0.1 + col * COLOFFSET, relwidth = ROWOFFSET, relheight = COLOFFSET)
                    
                    Label(room_label, text = str(room_number)).place(relx = 0.02, rely = 0.02, relwidth = 0.2, relheight = 0.1)
                    if not room_info['inGame']:
                        Button(room_label, text = 'join', command = join_click).place(relx = 0.65, rely = 0.7, relwidth = 0.25, relheight = 0.2)

                    counter += 1
                if len(room_numbers) > ROOMVIEW:
                    Button(frame, text = 'back', command = click_back).place(relx = 0.1, rely = 0.9, relwidth = 0.2, relheight = 0.05)
                    Button(frame, text = 'next', command = click_next).place(relx = 0.7, rely = 0.9, relwidth = 0.2, relheight = 0.05)

            frame.after(1000, refresh)
        refresh()


    def room_page(self):
        frame = Frame(self.root)
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

        data, prev_data = None, None
        error_message, error_label = None, None
        def refresh():
            nonlocal data, prev_data
            status_code, data = self.client.get_room_info()
            log_with_timestamp("Refreshed Room")
            if status_code != 200:
                frame.destroy()
                self.Error_page(status_code, data)
            else:
                if data != prev_data:
                    set_up_page()
                else:
                    frame.after(1000, refresh)
                prev_data = data

        def click_start():
            nonlocal error_message
            status_code, response = self.client.start_game()
            if status_code != 200:
                error_message = response['error']
                error_label.config(text = response['error'])

        def click_ready():
            nonlocal error_message
            status_code, response = self.client.user_ready()
            if status_code != 200:
                error_message = response['error']
                error_label.config(text = response['error'])
               
        def click_quit_room():
            status_code, response = self.client.quit_room()
            if status_code != 200:
                self.Error_page(status_code, response)
            else:
                frame.destroy()
                self.lobby_page()

        def set_up_page():
            log_with_timestamp("Setting up room!")
            nonlocal frame, error_label
            frame.destroy()
            if data['inGame']:
                self.root.after(30, self.game_page)
                return
                
            frame = Frame(self.root)
            frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)

            if data['hostname'] == self.client.username:
                ready_button = Button(frame, text = 'Start', command = click_start)
            else:
                txt = None
                for name, ready in data['user_info'].values():
                    if name == self.client.username:
                        txt = 'Cancel' if ready else "Ready"
                ready_button = Button(frame, text = txt, command = click_ready)
            ready_button.place(relx = 0.7, rely = 0.05, relwidth = 0.2, relheight = 0.05)

            users = data['user_info']
            for i in range(10):
                x_offset = i % 2
                y_offset = i // 2
                user_label = Label(frame, borderwidth = 2, relief = 'groove')
                user_label.place(relx = 0.1 + x_offset*0.4, rely = 0.1 + y_offset*0.16, relwidth = 0.4, relheight = 0.16)
                Label(user_label, text = str(i)).place(relx = 0.02, rely = 0.02, relwidth = 0.2, relheight = 0.2)
                if str(i) in users:
                    Label(user_label, borderwidth = 1, relief = 'groove', text = str(users[str(i)][0])).place(relx = 0.2, rely = 0.1, relwidth = 0.48, relheight = 0.8)
                    if users[str(i)][0] == data['hostname']:
                        ready_text = 'Host'
                    else:
                        ready_text = 'Ready' if users[str(i)][1] else 'Not Ready'
                    Message(user_label, borderwidth = 1, relief = 'groove', text = ready_text).place(relx = 0.7, rely = 0.1, relwidth = 0.28, relheight = 0.8)
                else:
                    Label(user_label, text = 'Empty').place(relx = 0.2, rely = 0.1, relwidth = 0.6, relheight = 0.8)

            error_label = Label(frame, text = error_message)
            error_label.place(relx = 0.1, rely = 0.05, relwidth = 0.6, relheight = 0.05)
            Button(frame, text = 'Quit Room', command = click_quit_room).place(relx = 0.1, rely = 0.9, relwidth = 0.3, relheight = 0.05)
            frame.after(1000, refresh)
        refresh()


    def game_page(self):
        frame = Frame(self.root)
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        status_code, meta_data = self.client.get_game_meta_data()
        if status_code != 200:
            self.Error_page(status_code, meta_data)

        player_num = meta_data['player_num']
        players_thumbnails = []
        player_card_nums = []
        cards, choice = [], None

        def gen_thumbnail(i, relx, rely):
            lab = Label(frame, text = meta_data[str(real_i(i))], borderwidth = 2, relief = 'groove')
            lab.place(relx = relx, rely = rely, relwidth = 0.1, relheight = 0.1)
            return lab
        def gen_card_num(relx, rely):
            lab = Label(frame)
            lab.place(relx = relx, rely = rely + 0.025, relwidth = 0.05, relheight = 0.05)
            return lab

        index_offset = meta_data['index']
        index_mod = meta_data['player_num']

        def real_i(i):
            return (i + index_offset) % index_mod

        def relative_i(i):
            return (i - index_offset) % index_mod

        players_thumbnails.append(gen_thumbnail(0, 0.45, 0.5))
        player_card_nums.append(gen_card_num(0.55, 0.5))

        side_num = player_num // 2 - 1 if player_num % 2 == 0 else player_num // 2
        space = (0.4 - side_num * 0.1) / (side_num + 1)

        for i in range(1, side_num + 1):
            players_thumbnails.append(gen_thumbnail(i, 0.05, 0.45 - (space + 0.1) * i))
            player_card_nums.append(gen_card_num(0.15, 0.45 - (space + 0.1) * i))

        if player_num % 2 == 0:
            players_thumbnails.append(gen_thumbnail(side_num + 1, 0.45, 0.05))
            player_card_nums.append(gen_card_num(0.55, 0.05))

        for i in range(1, side_num + 1):
            players_thumbnails.append(gen_thumbnail(player_num // 2 + i, 0.85, (space + 0.1) * i - 0.05))
            player_card_nums.append(gen_card_num(0.8, (space + 0.1) * i - 0.05))

        top_card = Label(frame)
        top_card.place(relx = 0.425, rely = 0.25, relwidth = 0.15, relheight = 0.2)

        def skip():
            nonlocal choice
            status_code, response = self.client.skip_card()
            if status_code != 200:
                return
            else:
                draw_button.config(text = 'draw', command = draw_card)
                destroy_color_choice()
                if choice:
                    cards[choice].place(relx = cards[choice].relx, rely = 0.75, relwidth = 0.15, relheight = 0.2)
                    choice = None
                draw_button.place_forget()
                play_button.place_forget()

        def draw_card():
            status_code, response = self.client.draw_card()
            if status_code != 200:
                return
            else:
                draw_button.config(text = 'skip', command = skip)

        def play_card():
            nonlocal choice
            card = Card(cards[choice].color, cards[choice].symbol)
            if not card.playable(Card(top_card.color, top_card.symbol)):
                cards[choice].place(relx = cards[choice].relx, rely = 0.75, relwidth = 0.15, relheight = 0.2)
                choice = None
                play_button['state'] = 'disable'
                destroy_color_choice()
            else:
                wild_color = color_choice if card.color in WILD_LIST else None
                status_code, response = self.client.play_card(card.color, card.symbol, wild_color)
                choice = None
                play_button['state'] = 'disable'
                draw_button.config(text = 'draw', command = draw_card)
                destroy_color_choice()
                draw_button.place_forget()
                play_button.place_forget()

        draw_button = Button(frame, text = 'draw', command = draw_card)
        play_button = Button(frame, text = 'play card', command = play_card)       
        play_button['state'] = 'disable'

        color_choices, color_choice = [], None
        data, prev_data = None, {}
        def refresh():
            nonlocal data, prev_data
            log_with_timestamp("Refreshed Game")
            status_code, data = self.client.get_game_info()
            if status_code != 200:
                frame.destroy()
                self.Error_page(status_code, data)
                return 
            if data['player_colors'][index_offset] != 'green':
                draw_button.place_forget()
                play_button.place_forget()
            else:
                draw_button.place(relx = 0.3, rely = 0.55, relwidth = 0.1, relheight = 0.05)
                play_button.place(relx = 0.6, rely = 0.55, relwidth = 0.15, relheight = 0.05)
            if data != prev_data:
                if data['game_end']:
                    frame.destroy()
                    messagebox.showinfo("Result", data['result'])
                    self.root.after(30, self.room_page)
                    return
                if data['player_colors'] != prev_data.get('player_colors', None):
                    for i in range(player_num):
                        players_thumbnails[i].config(bg = COLOR[data['player_colors'][real_i(i)]])
                if data['player_card_nums'] != prev_data.get('player_card_nums', None):
                    for i in range(player_num):
                        player_card_nums[i].config(text = str(data['player_card_nums'][real_i(i)]))
                if data['top_card'] != prev_data.get('top_card', None):
                    top_card.color = data['top_card'][0]
                    top_card.symbol = data['top_card'][1]
                    top_card.image = ImageTk.PhotoImage(IMAGE_DICT[top_card.color + top_card.symbol])
                    top_card.config(image = top_card.image)
                if data['cards'] != prev_data.get('cards', None):
                    for card in cards:
                        card.destroy()
                    gen_cards(data['cards'])
            prev_data = data
            check_resize()
            frame.after(1000, refresh)

        def check_resize():
            self.root.update()
            size = (int(frame.winfo_width()*0.15), int(frame.winfo_height()*0.2))
            def helper(card):
                if card.size != size:
                    name = card.color + card.symbol
                    IMAGE_DICT[name] = IMAGE_DICT[name].resize(size, Image.ANTIALIAS)
                    card.image = ImageTk.PhotoImage(IMAGE_DICT[name])
                    card.config(image = card.image)
            helper(top_card)
            for card in cards:
                helper(card)

            size = (int(frame.winfo_width()*0.03), int(frame.winfo_height()*0.03))
            for color in color_choices:
                if color.size != size:
                    name = color.color
                    IMAGE_DICT[name] = IMAGE_DICT[name].resize(size, Image.ANTIALIAS)
                    color.image = ImageTk.PhotoImage(IMAGE_DICT[name])
                    color.config(image = color.image)

        def make_choice(button):
            nonlocal color_choice
            for color in color_choices:
                color.config(text = "")
            if color_choice == button.color:
                color_choice = None
                play_button['state'] = 'disable'
            else:
                color_choice = button.color
                button.config(text = "X", compound = CENTER)
                play_button['state'] = 'normal'
      
        def built_color_choice():
            nonlocal color_choices
            image = ImageTk.PhotoImage(IMAGE_DICT['Red'])
            red_button = Button(frame, image = image)
            red_button.image = image
            red_button.color = 'Red'
            red_button.place(relx = 0.62, rely = 0.3, relwidth = 0.03, relheight = 0.03)
            red_button.config(command = lambda: make_choice(red_button))

            image = ImageTk.PhotoImage(IMAGE_DICT['Yellow'])
            yellow_button = Button(frame, image = image)
            yellow_button.image = image
            yellow_button.color = 'Yellow'
            yellow_button.place(relx = 0.62, rely = 0.35, relwidth = 0.03, relheight = 0.03)
            yellow_button.config(command = lambda: make_choice(yellow_button))
            
            image = ImageTk.PhotoImage(IMAGE_DICT['Blue'])
            blue_button = Button(frame, image = image)
            blue_button.image = image
            blue_button.color = 'Blue'
            blue_button.place(relx = 0.62, rely = 0.4, relwidth = 0.03, relheight = 0.03)
            blue_button.config(command = lambda: make_choice(blue_button))

            image = ImageTk.PhotoImage(IMAGE_DICT['Green'])
            green_button = Button(frame, image = image)
            green_button.image = image
            green_button.color = 'Green'
            green_button.place(relx = 0.62, rely = 0.45, relwidth = 0.03, relheight = 0.03)
            green_button.config(command = lambda: make_choice(green_button))

            color_choices = [red_button, yellow_button, blue_button, green_button]
            play_button['state'] = 'disable'

        def destroy_color_choice():
            nonlocal color_choices, color_choice
            for color in color_choices:
                color.destroy()
            color_choices, color_choice = [], None

        def gen_cards(card_name_list):
            nonlocal cards, choice
            card_name_list = sort_str_card_list(card_name_list)
            card_num = len(card_name_list)
            total_space = 0.9 - card_num * 0.15
            cards = []
            choice = None
            def pop_card(i):
                nonlocal choice
                if choice is not None:
                    cards[choice].place(relx = cards[choice].relx, rely = 0.75, relwidth = 0.15, relheight = 0.2)
                    destroy_color_choice()
                if choice == i:
                    choice = None
                    play_button['state'] = 'disable'
                else:
                    cards[i].place(relx = cards[i].relx, rely = 0.65, relwidth = 0.15, relheight = 0.2)
                    choice = i
                    if cards[choice].color in WILD_LIST:
                        built_color_choice()
                    else:
                        play_button['state'] = 'normal'

            def gen_card(i, relx, rely):
                image = ImageTk.PhotoImage(IMAGE_DICT[card_name_list[i][0] + card_name_list[i][1]])
                cards.append(Button(frame, image = image, command = lambda: pop_card(i)))
                cards[i].place(relx = relx, rely = rely, relwidth = 0.15, relheight = 0.2)
                cards[i].image = image
                cards[i].color = card_name_list[i][0]
                cards[i].symbol = card_name_list[i][1]
                cards[i].relx = relx

            if total_space > 0:
                space = total_space / (card_num + 1)
                for i in range(card_num):
                    gen_card(i, 0.05 + i * (0.15 + space) + space, 0.75)
            else:
                space = total_space / (card_num - 1)
                for i in range(card_num):
                    gen_card(i, 0.05 + i * (0.15 + space), 0.75)
        refresh()


    def server_down_page(self):
        frame = Frame(self.root)
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        Label(frame, text = "Server Down!", font = ("Times", 30)).place(relx = 0.25, rely = 0.25, relwidth = 0.5, relheight = 0.5)
    

    def Error_page(self, status_code, response):
        frame = Frame(self.root)
        frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 1)
        Message(frame, text = str(status_code) + ": "+ str(response['error'])).place(relx = 0.25, rely = 0.25, relwidth = 0.5, relheight = 0.5)
 

    def exit(self):
        if self.client:
            self.client.send_exit_signal()



if __name__ == '__main__':
    c = ClientGUI()
    atexit.register(lambda: c.exit())