import tkinter
import tkinter.ttk
import tkinter.tix
import tkinter.filedialog
import tkinter.messagebox
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
from PIL import ImageTk, Image

import objects
import widgets

root = tkinter.tix.Tk()
root.title('Fun Marathon')
root.iconbitmap('resources/dsicon.ico')
root.state('zoomed')

#######################################
# STARTUP
#######################################
ask_open = tkinter.Toplevel(root)
ask_open.title('Open Set..')
ask_open.resizable(False, False)
ask_open.grab_set()

file_destination = ''


def get_new_file():
    global file_destination, ask_open
    file_loc = tkinter.filedialog.asksaveasfilename() + '.fun_marathon'
    if file_loc != '.fun_marathon':
        file_destination = file_loc
        ask_open.grab_release()
        ask_open.quit()
        ask_open.destroy()


def load_new_file():
    global file_destination, ask_open
    file_loc = tkinter.filedialog.askopenfilename()
    if file_loc is not None:
        file_destination = file_loc
        ask_open.grab_release()
        ask_open.quit()
        ask_open.destroy()

tkinter.Label(ask_open, text='Would you like to load a previously saved set\n'
                             'or would want to create a new set?').grid(row=1, column=1, columnspan=2, padx=4, pady=4)

new_file = tkinter.ttk.Button(ask_open, text='New Set', command=get_new_file)
new_file.grid(row=2, column=1, padx=4, pady=4)
load_file = tkinter.ttk.Button(ask_open, text='Load Set', command=load_new_file)
load_file.grid(row=2, column=2, padx=4, pady=4)

ask_open.focus_set()
ask_open.mainloop()

#######################################
# FUNCTIONS AND VARIABLES
#######################################
connection = sqlite3.connect(file_destination)

connection.execute('''CREATE TABLE IF NOT EXISTS GAMES(
                    NAME        VARCHAR(63),
                    COORDINATOR VARCHAR(31));''')

connection.execute('''CREATE TABLE IF NOT EXISTS PLAYERS(
                    ID          INTEGER     NOT NULL    PRIMARY KEY AUTOINCREMENT,
                    NAME        VARCHAR(31) NOT NULL,
                    GENDER      VARCHAR(1),
                    CATEGORY    VARCHAR(1));''')

connection.execute('''CREATE TABLE IF NOT EXISTS SETTINGS(
                    THEME               TEXT        DEFAULT 'vista',
                    GRAPH               INTEGER     DEFAULT 1,
                    GRAPH_COLORS        TEXT        DEFAULT 'rbygc',
                    INDV_BOARD          INTEGER     DEFAULT 1,
                    MAIN_BOARD_LABEL    TEXT        DEFAULT 'Live Scores',
                    MAIN_BOARD_GAME_LIST_LABEL TEXT DEFAULT 'Individual Games Topper',
                    MAIN_BOARD_TOTAL_SCORES_LABEL TEXT DEFAULT 'Top Players based on All Games',
                    STRIPE_COLOR1       TEXT        DEFAULT '#a0e2ff',
                    STRIPE_COLOR2       TEXT        DEFAULT '#ffffff',
                    SCORE_UPDATION_DURATION INTEGER DEFAULT 10000
                    );''')

if list(connection.execute('SELECT * FROM SETTINGS;')) == []:
    connection.execute('INSERT INTO SETTINGS DEFAULT VALUES;')

field_values = connection.execute('SELECT * FROM SETTINGS;')
field_titles = [field[0].lower() for field in field_values.description]
field_values = list(field_values)[0]
settings = dict(zip(field_titles, field_values))


def create_game(name, coordinator, connection, new=True, game_data=None):
    if game_data is not None:
            game_data.destroy()

    game = objects.Game(name, coordinator, connection, new)

    if not game:
        return

    notebook.add(game.frame, text=game.name, underline=0, sticky=tkinter.NS)


def new_game(*ignore):
    game_data = tkinter.Toplevel(root)
    game_data.title('New Game...')
    game_data.grab_set()

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
    game_data.mainloop()


def get_results(connection):
    player_id = indv_id.get()

    try:
        games = list(connection.execute('SELECT NAME FROM GAMES;'))

        data = list(connection.execute('SELECT ID, NAME, %s FROM PLAYERS WHERE ID = %s' %
                                       (', '.join([process_name(item.__getitem__(0)) for item in games]), player_id)))[0]

        details = dict()
        details['id'] = data[0]
        details['name'] = data[1]

        for index in range(len(games)):
            details[games[index]] = data[index+2]

        return details

    except:
        tkinter.messagebox.showerror('Error!', 'An error has occured and we are not able to process your request.')


def change_settings(*ignore):
    objects.Settings(settings, root, connection)


def process_name(string):
    return 'game_' + string.replace(' ', '_').replace("'", '').replace('"', '')

#######################################
# MENU BAR
#######################################
root.title(root.title() + ' - ' + file_destination)
root.bind('<Control-n>', new_game)
root.bind('<Control-N>', new_game)
root.bind('<Insert>', new_game)
root.bind('<Control-s>', change_settings)
root.bind('<Control-S>', change_settings)

menu = tkinter.Menu(tearoff=False)

file_menu = tkinter.Menu(tearoff=False)
file_menu.add_command(label='New Game', command=new_game, accelerator='Ctrl + N / Insert')
file_menu.add_command(label='Refresh', command=lambda: refresh(connection), accelerator='Ctrl + R')
file_menu.add_separator()
file_menu.add_command(label='Exit', command=root.destroy)

settings_menu = tkinter.Menu(tearoff=False)
settings_menu.add_command(label='Settings', command=change_settings, accelerator='Ctrl + S')

menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Settings', menu=settings_menu)

root.config(menu=menu)

#######################################
# NOTEBOOK
#######################################
style = tkinter.ttk.Style()
style.theme_use(settings['theme'])
style.configure('Treeview', rowheight=40)
style.configure('Treeview.Heading', font=('Arial', 24), foreground='#006000')
style.configure('Treeview.Column', stretch=False)

notebook = tkinter.ttk.Notebook(root, height=root.winfo_screenheight(), width=root.winfo_screenwidth())
notebook.enable_traversal()
notebook.grid(row=1, column=1, padx=4, pady=4)

#######################################
# MAIN BOARD
#######################################
# TODO: Try to unite update_leader_tree and update_game_tree and reduce the runtime
main_board = tkinter.Frame()

img_tk = ImageTk.PhotoImage(Image.open('resources/50-ann2.jpg'))
tkinter.ttk.Label(main_board, text=settings['main_board_label'],
                  font=('Arial', 48)).grid(row=1, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

img_label = tkinter.Label(main_board, image=img_tk, compound=tkinter.RIGHT, anchor=tkinter.E)
img_label.grid(row=1, column=3, rowspan=2, sticky=tkinter.E)

tkinter.ttk.Label(main_board, text=settings['main_board_game_list_label'],
                  font=('Arial', 24)).grid(row=2, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

game_tree = tkinter.ttk.Treeview(main_board, columns=('Game', 'Coordinator', 'Played By',
                                                      'Max. Points Scored', 'Best Player'),
                                 show='headings', height=5, selectmode=tkinter.NONE)
game_tree.grid(row=3, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)
game_tree.heading('Game', text='Game')
game_tree.column('Game', width=320, anchor=tkinter.CENTER)
game_tree.heading('Coordinator', text='Coordinator')
game_tree.column('Coordinator', width=320, anchor=tkinter.CENTER)
game_tree.heading('Played By', text='Played By')
game_tree.column('Played By', width=240, anchor=tkinter.CENTER)
game_tree.heading('Max. Points Scored', text='Max. Points Scored')
game_tree.column('Max. Points Scored', width=320, anchor=tkinter.CENTER)
game_tree.heading('Best Player', text='Best Player')
game_tree.column('Best Player', width=320, anchor=tkinter.CENTER)


def update_game_tree(connection, self_called=True):
    game_tree.delete(*game_tree.get_children())

    columns = []

    for (game_name,) in connection.execute('SELECT NAME FROM GAMES;'):
        columns.append('COALESCE(%s, 0)' % (process_name(game_name).upper()))

    columns = ' + '.join(columns)

    if columns != '':
        row_number = 0

        for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
            played_by = connection.execute('SELECT COUNT(*) FROM PLAYERS WHERE ' +
                                           process_name(game_name) + ' IS NOT NULL').fetchall()

            max_player, max_score = connection.execute('SELECT NAME, %s FROM PLAYERS ORDER BY %s DESC, %s DESC LIMIT 1;' %
                                                       (process_name(game_name), process_name(game_name), columns)).fetchone() or (None, None)

            if max_score == None:
                max_player = None

            game_tree.insert('', tkinter.END, values=(game_name, game_coordinator, str(played_by[0][0]) + ' players',
                                                      max_score, max_player), tags=(str(row_number % 2),))
            row_number += 1

        game_tree.tag_configure('0', font=('Arial', 22), background=settings['stripe_color1'])
        game_tree.tag_configure('1', font=('Arial', 22), background=settings['stripe_color2'])

        if len(game_tree.get_children()) > game_tree.cget('height'):
            game_tree.config(height=len(game_tree.get_children()))

    if self_called:
        game_tree.after(settings['score_updation_duration'], lambda: update_game_tree(connection))


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


sort_by = tkinter.ttk.Labelframe(main_board, text='Filter Options')
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
    rank = 0

    fam = family.get()
    gen = gender.get()
    cat = category.get()
    if games_played != '':
        for player in connection.execute('SELECT ID, NAME, %s, %s FROM PLAYERS WHERE UPPER(GENDER) = UPPER(%s) AND CATEGORY = %s'
                                         ' ORDER BY %s DESC LIMIT 5;' % (games_played, columns, gen, cat, columns)):
            try:
                leader_tree.insert('', tkinter.END, values=((rank+1,) + player) + ('%.2f' % round(player[-1]/player[-2], 2),), tags=(str(rank % 2),))
                rank += 1
            except:
                pass

        leader_tree.tag_configure('0', font=('Arial', 12), background=settings['stripe_color1'])
        leader_tree.tag_configure('1', font=('Arial', 12), background=settings['stripe_color2'])

        if len(leader_tree.get_children()) > leader_tree.cget('height'):
            leader_tree.config(height=len(leader_tree.get_children()))

    if self_called:
        leader_tree.after(settings['score_updation_duration'], lambda: update_leader_tree(connection))

notebook.add(main_board, text=settings['main_board_label'], underline=0, sticky=tkinter.NS)

#######################################
# GRAPH
#######################################
if settings['graph']:
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

        if columns != '':
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
            root.after(settings['score_updation_duration'], lambda: update_graph(connection))

    notebook.add(graph_board, text='Graphs', underline=0, sticky=tkinter.NS)


def refresh(connection):
    update_game_tree(connection, False)
    update_leader_tree(connection, False)
    if settings['graph']:
        update_graph(connection, False)

root.bind('<Control-r>', lambda event: refresh(connection))
root.bind('<Control-R>', lambda event: refresh(connection))

#######################################
# SCORES MANAGER
#######################################
if True:
    score_manager = tkinter.Frame()

    tkinter.ttk.Label(score_manager, text='Score Manager', font=('Arial', 36)).grid(row=1, column=1, columnspan=2, padx=4, pady=4)

    score_tree = widgets.EditableTreeview(score_manager, show='headings')
    score_tree.grid(row=2, column=1, sticky=tkinter.NS)
    score_tree.bind('<<EditableTreeviewEdited>>', lambda event: update_database(event, connection))

    scroll_bar = tkinter.ttk.Scrollbar(score_manager, command=score_tree.yview)
    scroll_bar.grid(row=2, column=2, sticky=tkinter.NS, padx=4, pady=4)

    score_tree.config(yscrollcommand=scroll_bar.set)

    score_manager.grid_rowconfigure(2, weight=1)

    # TODO: The games score width in treeview in score manager getting awkard
    # TODO: Shift the function below this to widgets.py

    def update_database(event, connection):
        game_name = process_name(score_tree.cget('columns')[event.x])
        id = event.y

        connection.execute('UPDATE PLAYERS SET %s = %s WHERE ID = %s;' % (game_name, score_tree.widget.get(), id))
        connection.commit()

        update_score_manager(connection, self_called=False)


    def update_score_manager(connection, self_called=True):
        score_tree.delete(*score_tree.get_children())

        games = list(map(lambda item: item.__getitem__(0),
                         list(connection.execute('SELECT NAME FROM GAMES;'))))

        players_score_data = list(connection.execute('''SELECT ID, NAME, %s FROM PLAYERS;''' % (', '.join(list(map(process_name, games),)))))

        score_tree.config(columns=('ID', 'Name',) + tuple(games))

        score_tree.heading('ID', text='ID')
        score_tree.column('ID', width=128, stretch=False, anchor=tkinter.CENTER)
        score_tree.heading('Name', text='Name')
        score_tree.column('Name', width=256, stretch=False, anchor=tkinter.CENTER)

        for game_name in games:
            score_tree.heading(game_name, text=game_name)
            score_tree.column(game_name, width=256, stretch=False, anchor=tkinter.CENTER)

        for single_player_scores in players_score_data:
            score_tree.insert('', tkinter.END, values=single_player_scores, tags=((single_player_scores[0]+1) % 2,))
        print()
        for column in score_tree['columns']:
            print(score_tree.column(column))

        score_tree.tag_configure(0, font=('Arial', 12), background=settings['stripe_color1'])
        score_tree.tag_configure(1, font=('Arial', 12), background=settings['stripe_color2'])

        if self_called:
            score_tree.after(settings['score_updation_duration'], lambda: update_score_manager(connection))

    notebook.add(score_manager, text='Score Manager', underline=0, sticky=tkinter.NS)


#######################################
# INDIVIDUAL SCORES
#######################################
if settings['indv_board']:
    individual_board = tkinter.Frame()

    tkinter.ttk.Label(individual_board, text='Individual Scores', font=('Arial', 36)).grid(row=1, column=1, columnspan=3,
                                                                                           padx=4, pady=4)

    tkinter.ttk.Label(individual_board, text='ID:').grid(row=2, column=1, padx=4, pady=4)
    indv_id = tkinter.ttk.Entry(individual_board)
    indv_id.grid(row=2, column=2, padx=4, pady=4)

    indv_button = tkinter.ttk.Button(individual_board, text='Get Results',
                                     command=lambda: update_indv_board(get_results(connection)))
    indv_button.bind('<Enter>', lambda event: update_indv_board(get_results(connection)))
    indv_button.bind('<Return>', lambda event: update_indv_board(get_results(connection)))
    indv_button.grid(row=2, column=3, padx=4, pady=4)

    indv_scores_tree = tkinter.ttk.Treeview(individual_board, columns=('Key', 'Value'),
                                            show='headings', selectmode=tkinter.NONE)
    indv_scores_tree.heading('Key', text='Key')
    indv_scores_tree.column('Key', width=256, anchor=tkinter.CENTER)
    indv_scores_tree.heading('Value', text='Value')
    indv_scores_tree.column('Value', width=256, anchor=tkinter.CENTER)
    indv_scores_tree.grid(row=3, column=1, columnspan=3, padx=4, pady=4)


    def update_indv_board(details):
        if details != None:
            indv_scores_tree.delete(*indv_scores_tree.get_children())

            indv_scores_tree.insert('', tkinter.END, values=('ID', details.pop('id')), tags=(0,))
            indv_scores_tree.insert('', tkinter.END, values=('Name', details.pop('name')), tags=(1,))

            row_number = 2

            for key in details:
                indv_scores_tree.insert('', tkinter.END, values=(key, details[key]), tags=(row_number % 2,))
                row_number += 1

            indv_scores_tree.tag_configure(0, font=('Arial', 12), background=settings['stripe_color1'])
            indv_scores_tree.tag_configure(1, font=('Arial', 12), background=settings['stripe_color2'])

            indv_scores_tree.config(height=len(indv_scores_tree.get_children()))


    notebook.add(individual_board, text='Individual Scores', underline=0, sticky=tkinter.NS)


#######################################
# PRE-LAUNCH
#######################################
for (game_name, game_coordinator) in connection.execute('SELECT * FROM GAMES;'):
    create_game(game_name, game_coordinator, connection, new=False)

update_game_tree(connection)
update_leader_tree(connection)

if settings['graph']:
    update_graph(connection)

if True:
    update_score_manager(connection)

#######################################
# MAINLOOP
#######################################
root.mainloop()
