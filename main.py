import tkinter
import tkinter.ttk
import tkinter.filedialog
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

import objects

# //TODO Solve the errors which occur when the starting game list is empty

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

connection.execute('''CREATE TABLE IF NOT EXISTS GAMES(
                    NAME VARCHAR(63),
                    COORDINATOR VARCHAR(31));''')

connection.execute('''CREATE TABLE IF NOT EXISTS PLAYERS(
                    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    NAME VARCHAR(31) NOT NULL,
                    GENDER VARCHAR(1),
                    CATEGORY VARCHAR(1));''')

connection.execute('''CREATE TABLE IF NOT EXISTS SETTINGS(
                    THEME TEXT DEFAULT 'vista',
                    GRAPH BOOL DEFAULT TRUE,
                    GRAPH_COLORS TEXT DEFAULT 'rbygc',
                    MAIN_BOARD_LABEL TEXT DEFAULT 'LIVE SCORES',
                    MAIN_BOARD_INDV_SCORES_LABEL TEXT DEFAULT 'Individual Games Topper',
                    MAIN_BOARD_TOTAL_SCORES_LABEL TEXT DEFAULT 'Top Players based on All Games',
                    STRIPE_COLORS TEXT DEFAULT '#a0e2ff'
                    );''')

if list(connection.execute('SELECT * FROM SETTINGS;')) == []:
    connection.execute('INSERT INTO SETTINGS DEFAULT VALUES;')

field_values = connection.execute('SELECT * FROM SETTINGS;')
field_titles = [field[0].lower() for field in field_values.description]
field_values = list(field_values)[0]
settings  = dict(zip(field_titles, field_values))

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
style = tkinter.ttk.Style()
style.theme_use(settings['theme'])
style.configure("Treeview.Heading", font=('Arial', 16))

notebook = tkinter.ttk.Notebook(root, height=root.winfo_screenheight(), width=root.winfo_screenwidth())
notebook.enable_traversal()
notebook.grid(row=1, column=1, padx=4, pady=4)

#######################################
# MAIN BOARD
#######################################
main_board = tkinter.Frame()

tkinter.ttk.Label(main_board, text=settings['main_board_label'],
                  font=('Arial', 36)).grid(row=1, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)


tkinter.ttk.Label(main_board, text=settings['main_board_indv_scores_label'],
                  font=('Arial', 24)).grid(row=2, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

game_tree = tkinter.ttk.Treeview(main_board, columns=('Game', 'Coordinator', 'Played By', 'Maximum Points Scored', 'Best Player'),
                                 show='headings', height=5, selectmode=tkinter.NONE)
game_tree.grid(row=3, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)
game_tree.heading('Game', text='Game')
game_tree.column('Game', width=192, anchor=tkinter.CENTER)
game_tree.heading('Coordinator', text='Coordinator')
game_tree.column('Coordinator', width=192, anchor=tkinter.CENTER)
game_tree.heading('Played By', text='Played By')
game_tree.column('Played By', width=160, anchor=tkinter.CENTER)
game_tree.heading('Maximum Points Scored', text='Maximum Points Scored')
game_tree.column('Maximum Points Scored', width=160, anchor=tkinter.CENTER)
game_tree.heading('Best Player', text='Best Player')
game_tree.column('Best Player', width=192, anchor=tkinter.CENTER)


def update_game_tree(connection):
    game_tree.delete(*game_tree.get_children())

    columns = []

    for (game_name,) in connection.execute('SELECT NAME FROM GAMES;'):
        columns.append('COALESCE(%s, 0)' % (process_name(game_name).upper()))

    columns = ' + '.join(columns)

    row = 0

    for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
        played_by = connection.execute('SELECT COUNT(*) FROM PLAYERS WHERE ' +
                                       process_name(game_name) + ' IS NOT NULL').fetchall()

        max_player, max_score = connection.execute('SELECT NAME, %s FROM PLAYERS ORDER BY %s DESC, %s DESC LIMIT 1;' %
                                                   (process_name(game_name), process_name(game_name), columns)).fetchall()[0]

        game_tree.insert('', tkinter.END, values=(game_name, game_coordinator, str(played_by[0][0]) + ' players', max_score, max_player), tags=(str(row%2),))
        row += 1

    game_tree.tag_configure('0', font=('Arial, 12'))
    game_tree.tag_configure('1', font=('Arial, 12'))
    game_tree.tag_configure('0', background=settings['stripe_colors'])

    if len(game_tree.get_children()) > game_tree.cget('height'):
        game_tree.config(height=len(game_tree.get_children()))

    game_tree.after(10000, lambda: update_game_tree(connection))


tkinter.ttk.Label(main_board, text=settings['main_board_total_scores_label'],
                  font=('Arial', 24)).grid(row=4, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

leader_tree = tkinter.ttk.Treeview(main_board, columns=('Rank', 'ID', 'Name', 'Games Played', 'Score', 'Average'),
                                   show='headings', height=5, selectmode=tkinter.NONE)
leader_tree.grid(row=5, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)
leader_tree.heading('Rank', text='Rank')
leader_tree.column('Rank', width=128, anchor=tkinter.CENTER)
leader_tree.heading('ID', text='ID')
leader_tree.column('ID', width=128, anchor=tkinter.CENTER)
leader_tree.heading('Name', text='Name')
leader_tree.column('Name', width=192, anchor=tkinter.CENTER)
leader_tree.heading('Games Played', text='Games Played')
leader_tree.column('Games Played', width=160, anchor=tkinter.CENTER)
leader_tree.heading('Score', text='Score')
leader_tree.column('Score', width=128, anchor=tkinter.CENTER)
leader_tree.heading('Average', text='Average')
leader_tree.column('Average', width=128, anchor=tkinter.CENTER)


sort_by = tkinter.ttk.Labelframe(main_board, text='Sorting Options')
family = tkinter.StringVar(value='"BOTH"')
gender = tkinter.StringVar(value='"GENDER"')
category = tkinter.StringVar(value='"CATEGORY"')

tkinter.Radiobutton(sort_by, text='Both', variable=family, value='"BOTH"', indicatoron=False, width=8).grid(row=1, column=1, padx=4, pady=2)
tkinter.Radiobutton(sort_by, text='Somanis', variable=family, value='\'somani\'', indicatoron=False, width=8).grid(row=1, column=2, padx=4, pady=2)
tkinter.Radiobutton(sort_by, text='Bahetis', variable=family, value='\'baheti\'', indicatoron=False, width=8).grid(row=1, column=3, padx=4, pady=2)

tkinter.Radiobutton(sort_by, text='Both', variable=gender, value='"GENDER"', indicatoron=False, width=8, command=lambda: update_leader_tree(connection, False)).grid(row=2, column=1, padx=4, pady=2)
tkinter.Radiobutton(sort_by, text='Male', variable=gender, value='\'M\'', indicatoron=False, width=8, command=lambda: update_leader_tree(connection, False)).grid(row=2, column=2, padx=4, pady=2)
tkinter.Radiobutton(sort_by, text='Female', variable=gender, value='\'F\'', indicatoron=False, width=8, command=lambda: update_leader_tree(connection, False)).grid(row=2, column=3, padx=4, pady=2)

tkinter.Radiobutton(sort_by, text='Both', variable=category, value='"CATEGORY"', indicatoron=False, width=8, command=lambda: update_leader_tree(connection, False)).grid(row=3, column=1, padx=4, pady=2)
tkinter.Radiobutton(sort_by, text='Adults', variable=category, value='\'A\'', indicatoron=False, width=8, command=lambda: update_leader_tree(connection, False)).grid(row=3, column=2, padx=4, pady=2)
tkinter.Radiobutton(sort_by, text='Kids', variable=category, value='\'K\'', indicatoron=False, width=8, command=lambda: update_leader_tree(connection, False)).grid(row=3, column=3, padx=4, pady=2)

sort_by.grid(row=6, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4, sticky=tkinter.NS)


def update_leader_tree(connection, self_called=True):
    leader_tree.delete(*leader_tree.get_children())

    columns = []
    games_played = []

    for item in connection.execute('SELECT NAME FROM GAMES;').fetchall():
        columns.append('COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)')
        games_played.append('(CASE WHEN %s IS NULL THEN 0 ELSE 1 END)' % (process_name(item.__getitem__(0))))

    columns = ' + '.join(columns)
    games_played = ' + '.join(games_played)
    rank = 1

    fam = family.get()
    gen = gender.get()
    cat = category.get()

    for player in connection.execute('SELECT ID, NAME, %s, %s FROM PLAYERS WHERE UPPER(GENDER) = UPPER(%s) AND CATEGORY = %s'
                                     ' ORDER BY %s DESC LIMIT 5;' % (games_played, columns, gen, cat, columns)):
        try:
            leader_tree.insert('', tkinter.END, values=((rank,) + player) + ('%.2f' % round(player[-1]/player[-2], 2),), tags=(str(rank%2),))
            rank += 1
        except:
            pass

    leader_tree.tag_configure('0', font=('Arial, 12'))
    leader_tree.tag_configure('1', font=('Arial, 12'))
    leader_tree.tag_configure('1', background=settings['stripe_colors'])

    if len(leader_tree.get_children()) > leader_tree.cget('height'):
        leader_tree.config(height=len(leader_tree.get_children()))

    if self_called:
        leader_tree.after(10000, lambda: update_leader_tree(connection))

notebook.add(main_board, text='Results', underline=0, sticky=tkinter.NS)

#######################################
# GRAPH
#######################################
graph_board = tkinter.Frame()
figure = Figure(figsize=(16, 7.5), dpi=100)
figure.subplots_adjust(left=0.05, right=0.90, top=0.95, bottom=0.1)

graph = figure.add_subplot(111)

canvas = FigureCanvasTkAgg(figure, master=graph_board)
canvas.show()
canvas.get_tk_widget().grid(row=3, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

def update_graph(connection, self_called=True):
    global graph
    columns = []
    for item in connection.execute('SELECT NAME FROM GAMES;').fetchall():
        columns.append('COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)')

    num_of_cols = len(columns)

    columns = ' + '.join(columns)

    figure.delaxes(graph)
    graph = figure.add_subplot(111, title='Results by ID', xlabel='Player by ID', ylabel='Player Score')
    score_data = list(connection.execute('SELECT ID, %s FROM PLAYERS;' % (columns,)))

    if score_data != []:
        ids, scores = zip(*score_data)
        graph.bar(ids, scores, color=settings['graph_colors'], align='center')

        graph.set_xlim([100, 150])
        graph.set_ylim([0, num_of_cols*10])
        x_loc = MultipleLocator(2)
        y_loc = MultipleLocator(2)
        graph.xaxis.set_major_locator(x_loc)
        graph.yaxis.set_major_locator(y_loc)

        graph.axhline(sum(scores)/len(scores), color='black', linestyle='dashed', linewidth=2)

    canvas.show()
    canvas.get_tk_widget().grid(row=3, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

    if self_called:
        root.after(10000, lambda: update_graph(connection))

notebook.add(graph_board, text='Graphs', underline=0, sticky=tkinter.NS)

#######################################
# PRE-LAUNCH
#######################################
for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
    create_game(game_name, game_coordinator, connection, new=False)

update_game_tree(connection)
update_leader_tree(connection)
update_graph(connection)

#######################################
# MAINLOOP
#######################################
root.mainloop()
