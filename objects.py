import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.colorchooser
import sqlite3

#######################################
# FUNCTIONS AND VARIBLES
#######################################
def process_name(string):
    return 'game_' + string.replace(' ', '_').replace("'", '').replace('"', '')

def choose_color(widget):
    color = tkinter.colorchooser.askcolor('light blue')
    widget.config(background=color[-1])


class Game(object):
    def __init__(self, name, coordinator, connection, new=True):
        '''
        The Game class is the object representing a singles game.
        It is a single game which may be played by a team or an individual.
        The scores of many games are used to show the score on the Results page.
        :param name: name of the game to be shown to the users; 
        :param coordinator: name of the coordinator of the game; not necessary
        :param connection: connection to the SQLite3 Database
        :param new: is the record new or bringing in from a previously saved game
        :return: None
        '''

        #######################################
        # FIRST SETTINGS
        #######################################
        self.name = name
        self.coordinator = coordinator

        #######################################
        # DATABASE
        #######################################
        if new:
            connection.execute('ALTER TABLE PLAYERS ADD ' + process_name(self.name) + ' INTEGER;')
            connection.execute('INSERT INTO GAMES VALUES(?, ?);', (name, coordinator))
            connection.commit()

        #######################################
        # FRAME
        #######################################
        self.frame = tkinter.Frame()

        tkinter.Label(self.frame, text=(self.name+' by '+self.coordinator),
                      font=('Arial', 36)).grid(row=1, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

        self.tree = tkinter.ttk.Treeview(self.frame, columns=('ID', 'Name', 'Score'), show='headings',
                                         height=5, selectmode=tkinter.NONE)
        self.tree.grid(row=2, column=1, columnspan=3, padx=4, pady=8, ipadx=4, ipady=4)
        self.tree.heading('ID', text="ID")
        self.tree.column("ID", width=96, anchor=tkinter.CENTER)
        self.tree.heading('Name', text="Name")
        self.tree.column("Name", width=256, anchor=tkinter.CENTER)
        self.tree.heading('Score', text="Score")
        self.tree.column("Score", width=96, anchor=tkinter.CENTER)

        tkinter.Label(self.frame, text='ID:', font=('Courier New', 16, 'bold')).grid(row=4, column=1)
        self.id = tkinter.Entry(self.frame, width=8, font=('Courier New', 16, 'bold'))
        self.id.grid(row=5, column=1, padx=4)

        tkinter.Label(self.frame, text='Points:', font=('Courier New', 16, 'bold')).grid(row=4, column=2)
        self.score = tkinter.Entry(self.frame, width=8, font=('Courier New', 16, 'bold'))
        self.score.grid(row=5, column=2, padx=4)

        self.submit = tkinter.ttk.Button(self.frame, text='Submit', command=lambda: self.add_score(connection))
        self.submit.bind('<Enter>', lambda event: self.add_score(connection))
        self.submit.bind('<Return>', lambda event: self.add_score(connection))
        self.submit.grid(row=5, column=3, padx=4)

        self.frame.bind('<Button-3>', self.show_menu)

        #######################################
        # MENU
        #######################################
        self.menu = tkinter.Menu(tearoff=False)
        self.menu.add_command(label='Rename', command=self.rename)
        self.menu.add_command(label='Destroy', command=lambda: self.destroy(connection))

        self.update_leaderboard(connection)

        self.warner = tkinter.Label(self.frame)
        self.warner.grid(row=6, column=1, columnspan=3)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def add_score(self, connection):
        player_id = self.id.get()
        player_score = self.score.get()

        if player_score == '' or int(player_score) < 0 or int(player_score) > 10:
            self.warner.config(text='Score Error!')
            self.score.bind()
            return

        try:
            connection.execute('UPDATE PLAYERS SET %s = %s WHERE ID = %s;' %
                               (process_name(self.name), player_score, player_id))
            connection.commit()
        except sqlite3.OperationalError as error:
            self.warner.config(text='SQLite Error: '+str(error))

        self.update_leaderboard(connection)

        self.id.delete(0, tkinter.END)
        self.score.delete(0, tkinter.END)

        self.id.focus_set()

    def rename(self):
        pass

    def destroy(self, connection):
        to_delete = tkinter.messagebox.askyesno('Delete Game', 'Are you sure you want to delete this game? '
                                                               'This action is irreversible.')

        if to_delete:
            connection.execute('DELETE FROM GAMES WHERE NAME = "' + self.name + '";')
            connection.commit()
            self.frame.destroy()

    def update_leaderboard(self, connection):
        self.tree.delete(*self.tree.get_children())

        columns = []
        for item in connection.execute('SELECT NAME FROM GAMES;').fetchall():
            columns.append('COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)')

        columns = ' + '.join(columns)

        for (id, player, score) in connection.execute('SELECT ID, NAME, %s FROM PLAYERS ORDER BY %s DESC, %s DESC LIMIT 5' %
                                                      (process_name(self.name), process_name(self.name), columns)):
            self.tree.insert('', tkinter.END, values=(id, player, score))


class Settings:
    def __init__(self, settings, root, connection):
        '''
        This class contains a Settings Toplevel and manages and changes all the settings.
        :param settings: a Settings dictionary
        :param root: master, the base Tk()
        :param connection: connection to sqlite3 database
        :return:
        '''
        #######################################
        # FIRST SETTINGS
        #######################################
        self.settings = settings

        #######################################
        # SETTINGS ROOT MODELLING
        #######################################
        self.subroot = tkinter.Toplevel(root)
        self.subroot.title('Settings')
        self.subroot.resizable(False, False)

        self.import_settings = tkinter.ttk.Button(self.subroot, text='Import Settings')
        self.import_settings.grid(row=1, column=1, columnspan=4, padx=4, pady=4, ipadx=4, ipady=4)

        self.main_page_settings = tkinter.ttk.LabelFrame(self.subroot, text='Main Page Settings')
        self.main_page_settings.grid(row=2, column=1, columnspan=4, padx=4, pady=4, ipadx=4, ipady=4)

        tkinter.Label(self.main_page_settings, text='Main Board Heading:').grid(row=1, column=1)
        self.main_board_label = tkinter.Entry(self.main_page_settings, width=32)
        self.main_board_label.insert(0, settings['main_board_label'])
        self.main_board_label.grid(row=1, column=2)

        tkinter.Label(self.main_page_settings, text='Main Board Games List Heading:').grid(row=2, column=1)
        self.main_board_game_list_label = tkinter.Entry(self.main_page_settings, width=32)
        self.main_board_game_list_label.insert(0, settings['main_board_game_list_label'])
        self.main_board_game_list_label.grid(row=2, column=2)

        tkinter.Label(self.main_page_settings, text='Main Board Total Scores Heading:').grid(row=3, column=1)
        self.main_board_total_scores_label = tkinter.Entry(self.main_page_settings, width=32)
        self.main_board_total_scores_label.insert(0, settings['main_board_total_scores_label'])
        self.main_board_total_scores_label.grid(row=3, column=2)

        tkinter.Label(self.main_page_settings, text='Stripe Color 1:').grid(row=4, column=1)
        self.stripe1 = tkinter.Label(self.main_page_settings, width=24, bg=settings['stripe_color1'])
        self.stripe1.bind('<Double-Button-1>', lambda event: choose_color(self.stripe1))
        self.stripe1.grid(row=4, column=2)

        tkinter.Label(self.main_page_settings, text='Stripe Color 2:').grid(row=5, column=1)
        self.stripe2 = tkinter.Label(self.main_page_settings, width=24, bg=settings['stripe_color2'])
        self.stripe2.bind('<Double-Button-1>', lambda event: choose_color(self.stripe2))
        self.stripe2.grid(row=5, column=2)

        self.graph_settings = tkinter.ttk.LabelFrame(self.subroot, text='Graph Settings')
        self.graph_settings.grid(row=3, column=1, columnspan=4, sticky=tkinter.EW, padx=4, pady=4, ipadx=4, ipady=4)

        tkinter.Label(self.graph_settings, text='Show Graph:').grid(row=1, column=1)
        self.graph_toggle = tkinter.IntVar(value=settings['graph'])
        self.show_graph = tkinter.Checkbutton(self.graph_settings, variable=self.graph_toggle)
        self.show_graph.grid(row=1, column=2)

        tkinter.Label(self.graph_settings, text='Graph Colors:').grid(row=2, column=1)
        self.graph_colors = tkinter.Entry(self.graph_settings)
        self.graph_colors.insert(0, settings['graph_colors'])
        self.graph_colors.grid(row=2, column=2)

        ok = tkinter.ttk.Button(self.subroot, text='OK', command=lambda: self.update(connection))
        ok.grid(row=10, column=1, columnspan=4, padx=4, pady=4, ipadx=4, ipady=4)

        self.subroot.focus_set()

    def update(self, connection):
        connection.execute('''UPDATE SETTINGS SET
                            THEME = ?,
                            GRAPH = ?,
                            GRAPH_COLORS = ?,
                            MAIN_BOARD_LABEL = ?,
                            MAIN_BOARD_GAME_LIST_LABEL = ?,
                            MAIN_BOARD_TOTAL_SCORES_LABEL = ?,
                            STRIPE_COLOR1 = ?,
                            STRIPE_COLOR2 = ?;''',
                           ('vista',
                            self.graph_toggle.get(),
                            self.graph_colors.get(),
                            self.main_board_label.get(),
                            self.main_board_game_list_label.get(),
                            self.main_board_total_scores_label.get(),
                            self.stripe1.cget('background'),
                            self.stripe2.cget('background')))
        connection.commit()
        self.subroot.destroy()
        tkinter.messagebox.showinfo('Changes Made',
                                    'The changes have been made.\nPlease restart the application for the changes to take effect.')
