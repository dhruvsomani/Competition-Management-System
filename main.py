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

        if not game:
            return

        notebook.add(game.frame, text=game.name, underline=0, sticky=tkinter.NS)

        if game_data is not None:
            game_data.destroy()


def new_game(*ignore):
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


def process_name(string):
    return 'game_' + string.replace(' ', '_').replace("'", '').replace('"', '')

#######################################
# MENU BAR
#######################################
root = tkinter.Tk()
root.title('Fun Marathon')
root.iconbitmap('dsicon.ico')
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
# MAIN BOARD
#######################################
main_board = tkinter.Frame()

tkinter.Label(main_board, text='Main Board',
              font=('Arial', 36)).grid(row=1, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)


tkinter.Label(main_board, text='Games',
              font=('Arial', 24)).grid(row=2, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

game_tree = tkinter.ttk.Treeview(main_board, columns=('Game', 'Coordinator', 'Played By', 'Maximum Score'),
                                 show='headings', height=5, selectmode=tkinter.NONE)
game_tree.grid(row=3, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)
game_tree.heading('Game', text='Game')
game_tree.column('Game', width=192, anchor=tkinter.CENTER)
game_tree.heading('Coordinator', text='Coordinator')
game_tree.column('Coordinator', width=192, anchor=tkinter.CENTER)
game_tree.heading('Played By', text='Played By')
game_tree.column('Played By', width=96, anchor=tkinter.CENTER)
game_tree.heading('Maximum Score', text='Maximum Score')
game_tree.column('Maximum Score', width=96, anchor=tkinter.CENTER)
game_tree.after(10000, lambda: update_game_tree(connection))


def update_game_tree(connection):
    game_tree.delete(*game_tree.get_children())
    for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
        played_by = connection.execute('SELECT COUNT(*) FROM PLAYERS WHERE ' +
                                       process_name(game_name) + ' IS NOT NULL').fetchall()
        max_score = connection.execute('SELECT MAX(' + process_name(game_name) + ') FROM PLAYERS;').fetchall()
        game_tree.insert('', tkinter.END, values=(game_name, game_coordinator, played_by[0], max_score[0]))
    if len(game_tree.get_children()) > game_tree.cget('height'):
        game_tree.config(height=len(game_tree.get_children()))
    game_tree.after(10000, lambda: update_game_tree(connection))


tkinter.Label(main_board, text='Top Players',
              font=('Arial', 24)).grid(row=4, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

leader_tree = tkinter.ttk.Treeview(main_board, columns=('Rank', 'ID', 'Name', 'Score', 'Average'),
                                   show='headings', height=5, selectmode=tkinter.NONE)
leader_tree.grid(row=5, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)
leader_tree.heading('Rank', text='Rank')
leader_tree.column('Rank', width=96, anchor=tkinter.CENTER)
leader_tree.heading('ID', text='ID')
leader_tree.column('ID', width=96, anchor=tkinter.CENTER)
leader_tree.heading('Name', text='Name')
leader_tree.column('Name', width=256, anchor=tkinter.CENTER)
leader_tree.heading('Score', text='Score')
leader_tree.column('Score', width=96, anchor=tkinter.CENTER)
leader_tree.heading('Average', text='Average')
leader_tree.column('Average', width=96, anchor=tkinter.CENTER)


def update_leader_tree(connection):
    leader_tree.delete(*leader_tree.get_children())
    columns = ['COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)' for item in connection.execute('SELECT NAME FROM GAMES;').fetchall()]
    num_of_games = len(columns)
    columns = '(' + ' + '.join(columns) + ')'
    for player in connection.execute('SELECT ROWID, ID, NAME,' + columns +
                                             ' FROM PLAYERS ORDER BY ' + columns + 'DESC LIMIT 5;'):
        leader_tree.insert('', tkinter.END, values=(player + (round(player[-1]/num_of_games, 2),)))
    if len(leader_tree.get_children()) > leader_tree.cget('height'):
        leader_tree.config(height=len(leader_tree.get_children()))
    leader_tree.after(10000, lambda: update_leader_tree(connection))

# tkinter.Label(self.frame, text='ID:', font=('Courier New', 16, 'bold')).grid(row=4, column=1)
# self.id = tkinter.Entry(self.frame, width=8, font=('Courier New', 16, 'bold'))
# self.id.grid(row=5, column=1, padx=4)
#
# tkinter.Label(self.frame, text='Points:', font=('Courier New', 16, 'bold')).grid(row=4, column=2)
# self.score = tkinter.Entry(self.frame, width=8, font=('Courier New', 16, 'bold'))
# self.score.grid(row=5, column=2, padx=4)
#
# self.submit = tkinter.ttk.Button(self.frame, text='Submit', command=lambda: self.add_score(connection))
# self.submit.bind('<Enter>', lambda event: self.add_score(connection))
# self.submit.bind('<Return>', lambda event: self.add_score(connection))
# self.submit.grid(row=5, column=3, padx=4)

notebook.add(main_board, text='Main Board', underline=0, sticky=tkinter.NS)

#######################################
# PRE-LAUNCH
#######################################
for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
    create_game(game_name, game_coordinator, connection, new=False)

update_game_tree(connection)
update_leader_tree(connection)


#######################################
# MAINLOOP
#######################################
root.mainloop()
