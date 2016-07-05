import tkinter
import tkinter.ttk
import tkinter.messagebox
import sqlite3


def process_name(string):
    return 'game_' + string.replace(' ', '_').replace("'", '').replace('"', '')


class Game(object):
    def __init__(self, name, coordinator, connection, new=True):
        #######################################
        # FIRST SETTINGS
        #######################################
        self.name = name
        self.coordinator = coordinator

        #######################################
        # DATABASE
        #######################################
        if new:
            try:
                connection.execute('INSERT INTO GAMES VALUES(?, ?);', (name, coordinator))
                connection.execute('ALTER TABLE PLAYERS ADD ' + process_name(self.name) + ' INTEGER;')
                connection.commit()
            except:
                pass

        #######################################
        # FRAME
        #######################################
        self.frame = tkinter.Frame()

        tkinter.Label(self.frame, text=(self.name+' by '+self.coordinator),
                      font=('Arial', 36)).grid(row=1, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)

        self.tree = tkinter.ttk.Treeview(self.frame, columns=('ID', 'Name', 'Score'), show='headings')
        self.tree.grid(row=2, column=1, columnspan=3, padx=4, pady=4, ipadx=4, ipady=4)
        self.tree.heading('ID', text="ID")
        self.tree.column("ID", width=96, anchor=tkinter.CENTER)
        self.tree.heading('Name', text="Name")
        self.tree.column("Name", width=128, anchor=tkinter.CENTER)
        self.tree.heading('Score', text="Score")
        self.tree.column("Score", width=128, anchor=tkinter.CENTER)

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
        self.menu.add_command(label='Destroy', command=lambda: self.destroy(connection))

        self.update_leaderboard(connection)

        self.warner = tkinter.Label(self.frame)
        self.warner.grid(row=6, column=1, columnspan=3)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def destroy(self, connection):
        to_delete = tkinter.messagebox.askyesno('Delete Game', 'Are you sure you want to delete this game?'
                                                               'This action is irreversible.')

        if to_delete:
            connection.execute('DELETE FROM GAMES WHERE NAME = ' + self.name + ';')
            connection.execute('ALTER TABLE PLAYERS DROP COLUMN ' + process_name(self.name) + ';')
            connection.commit()
            self.frame.destroy()

    def add_score(self, connection):
        player_id = self.id.get()
        player_game = self.name
        player_score = self.score.get()

        if player_score == '' or int(player_score) < 0 or int(player_score) > 10:
            self.warner.config(text='Score Error!')
            self.score.bind()
            return

        try:
            connection.execute('UPDATE PLAYERS SET ' + process_name(player_game) + ' = ' + player_score + ' WHERE ID = ' + player_id + ';')
            connection.commit()
        except sqlite3.OperationalError as error:
            self.warner.config(text='SQLite Error: '+str(error))

        self.update_leaderboard(connection)

        self.id.delete(0, tkinter.END)
        self.score.delete(0, tkinter.END)

    def update_leaderboard(self, connection):
        self.tree.delete(*self.tree.get_children())
        for (id, player, score) in connection.execute('SELECT ID, NAME, ' + process_name(self.name) + ' FROM PLAYERS ORDER BY ' + process_name(self.name) + ' DESC LIMIT 3'):
            self.tree.insert('', tkinter.END, values=(id, player, score))
