import tkinter
import tkinter.ttk
import tkinter.tix
import tkinter.filedialog
import sqlite3
import objects

#######################################
# STARTUP
#######################################
# ask_open = tkinter.Tk()
# ask_open.title('Open Set..')
# ask_open.resizable(False, False)
#
# file_destination = ''
#
#
# def get_new_file():
#     global file_destination, ask_open
#     file_loc = tkinter.filedialog.asksaveasfilename()
#     if file_loc is not None:
#         file_destination = file_loc
#         ask_open.destroy()
#
#
# def load_new_file():
#     global file_destination, ask_open
#     file_loc = tkinter.filedialog.askopenfilename()
#     if file_loc is not None:
#         file_destination = file_loc
#         ask_open.destroy()
#
#
# tkinter.Label(ask_open, text='Would you like to load a previously saved set\n'
#                              'or would want to create a new set?').grid(row=1, column=1, columnspan=2, padx=4, pady=4)
#
# new_file = tkinter.ttk.Button(ask_open, text='New Set', command=get_new_file)
# new_file.grid(row=2, column=1, padx=4, pady=4)
# load_file = tkinter.ttk.Button(ask_open, text='Load Set', command=load_new_file)
# load_file.grid(row=2, column=2, padx=4, pady=4)


#######################################
# FUNCTIONS AND VARIABLES
#######################################
connection = sqlite3.connect('D:/fun_marathon.sqlite3')

connection.execute('''CREATE TABLE IF NOT EXISTS GAMES (
                    NAME VARCHAR(63),
                    COORDINATOR VARCHAR(31));''')

connection.execute('''CREATE TABLE IF NOT EXISTS PLAYERS (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    NAME VARCHAR(31) NOT NULL,
                    SURNAME VARCHAR(31),
                    GENDER VARCHAR(1),
                    CATEGORY VARCHAR(1));''')

def create_game(name, coordinator, connection, new=True, game_data=None):
        game = objects.Game(name, coordinator, connection, new)
        if game == False:
            return

        notebook.add(game.frame, text=game.name, underline=0, sticky=tkinter.NS)

        if game_data is not None:
            game_data.destroy()


def new_game(event=None):
    game_data = tkinter.Toplevel(root)
    game_data.title('New Game...')

    tkinter.Label(game_data, text='Name:').grid(row=1, column=1, padx=4, pady=4)
    name = tkinter.Entry(game_data)
    name.grid(row=1, column=2, padx=4, pady=4)

    tkinter.Label(game_data, text='Coordinator:').grid(row=2, column=1, padx=4, pady=4)
    coordinator = tkinter.Entry(game_data)
    coordinator.grid(row=2, column=2, padx=4, pady=4)

    submit = tkinter.ttk.Button(game_data, text='Submit',
                                command=lambda: create_game(name.get(), coordinator.get(),
                                                            connection, game_data=game_data))
    submit.bind('<Enter>', lambda event: create_game(name.get(), coordinator.get(), connection, game_data=game_data))
    submit.bind('<Return>', lambda event: create_game(name.get(), coordinator.get(), connection, game_data=game_data))
    submit.grid(row=3, column=1, columnspan=2)

    name.focus_set()

#######################################
# MENU BAR
#######################################
root = tkinter.Tk()
root.title('Fun Marathon')
root.state('zoomed')
root.bind('<Control-n>', new_game)
root.bind('<Control-N>', new_game)

menu = tkinter.Menu(tearoff=False)

file_menu = tkinter.Menu(tearoff=False)
file_menu.add_command(label='New Game', command=new_game)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=root.destroy)

menu.add_cascade(label='File', menu=file_menu)

root.config(menu=menu)

#######################################
# NOTEBOOK
#######################################
notebook = tkinter.ttk.Notebook(root, height=root.winfo_screenheight(), width=root.winfo_screenwidth())
notebook.enable_traversal()
notebook.grid(row=1, column=1, padx=4, pady=4)

#######################################
# PRE-LAUNCH
#######################################
for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
    create_game(game_name, game_coordinator, connection, new=False)


#######################################
# MAINLOOP
#######################################
root.mainloop()
