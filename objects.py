import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.colorchooser
import sqlite3

#######################################
# FUNCTIONS AND VARIBLES
#######################################
def process_name(string):
	return 'game_' + string.replace(' ', '_').replace("'", '').replace('"', '')

#######################################
# OBJECTS AND CLASSES
#######################################
class Game(object):
	def __init__(self, name, coordinator, connection, new=True):
		'''
		The Game class is the object representing a single game.
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
			connection.execute('ALTER TABLE PLAYERS ADD \'' + process_name(self.name) + '\' INTEGER;')
			connection.execute('INSERT INTO GAMES VALUES(?, ?);', (name, coordinator))
			connection.commit()

		#######################################
		# FRAME
		#######################################
		self.frame = tkinter.Frame()

		tkinter.Label(self.frame, text=(self.name),
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

		try:
			for (id, player, score) in connection.execute('SELECT ID, NAME, %s FROM PLAYERS ORDER BY %s DESC, %s DESC LIMIT 5' %
														  (process_name(self.name), process_name(self.name), columns)):
				self.tree.insert('', tkinter.END, values=(id, player, score))
		except:
			pass


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

		self.import_settings = tkinter.ttk.Button(self.subroot, text='Import Settings from an other game', command=lambda: self.import_sets(connection))
		self.import_settings.grid(row=1, column=1, columnspan=4, padx=4, pady=4)

		self.main_page_settings = tkinter.ttk.LabelFrame(self.subroot, text='Main Page Settings')
		self.main_page_settings.grid(row=2, column=1, columnspan=4, padx=4, pady=4, ipadx=4, ipady=4)

		tkinter.Label(self.main_page_settings, text='Title:').grid(row=1, column=1, padx=2, pady=2)
		self.main_board_label = tkinter.ttk.Entry(self.main_page_settings, width=32)
		self.main_board_label.insert(0, settings['mainboard_label'])
		self.main_board_label.grid(row=1, column=2, padx=2, pady=2)

		tkinter.Label(self.main_page_settings, text='Leaderboard Title:').grid(row=3, column=1, padx=2, pady=2)
		self.main_board_total_scores_label = tkinter.ttk.Entry(self.main_page_settings, width=32)
		self.main_board_total_scores_label.insert(0, settings['leaderboard_label'])
		self.main_board_total_scores_label.grid(row=3, column=2, padx=2, pady=2)

		tkinter.Label(self.main_page_settings, text='Number of Ranks:').grid(row=4, column=1, padx=2, pady=2)
		self.num_of_ranks = tkinter.ttk.Entry(self.main_page_settings, width=32)
		self.num_of_ranks.insert(0, settings['num_of_ranks'])
		self.num_of_ranks.grid(row=4, column=2, padx=2, pady=2)

		tkinter.Label(self.main_page_settings, text='Stripe Color 1:').grid(row=5, column=1, padx=2, pady=2)
		self.stripe1 = tkinter.ttk.Label(self.main_page_settings, width=24, background=settings['stripe_color1'])
		self.stripe1.bind('<Double-Button-1>', lambda event: self.choose_color(self.stripe1))
		self.stripe1.grid(row=5, column=2, padx=2, pady=2)

		tkinter.Label(self.main_page_settings, text='Stripe Color 2:').grid(row=6, column=1)
		self.stripe2 = tkinter.ttk.Label(self.main_page_settings, width=24, background=settings['stripe_color2'])
		self.stripe2.bind('<Double-Button-1>', lambda event: self.choose_color(self.stripe2))
		self.stripe2.grid(row=6, column=2, padx=2, pady=2)

		tkinter.ttk.Label(self.main_page_settings, text='Score Updation Duration (ms):').grid(row=7, column=1, padx=2, pady=2)
		self.score_updation_duration = tkinter.ttk.Entry(self.main_page_settings)
		self.score_updation_duration.insert(0, settings['score_updation_duration'])
		self.score_updation_duration.grid(row=7, column=2, padx=2, pady=2)

		self.graph_settings = tkinter.ttk.LabelFrame(self.subroot, text='Graph Settings')
		self.graph_settings.grid(row=3, column=1, columnspan=4, sticky=tkinter.EW, padx=4, pady=4, ipadx=4, ipady=4)

		tkinter.Label(self.graph_settings, text='Show Graph:').grid(row=1, column=1, padx=2, pady=2)
		self.graph_toggle = tkinter.IntVar(value=settings['graph'])
		self.show_graph = tkinter.ttk.Checkbutton(self.graph_settings, variable=self.graph_toggle)
		self.show_graph.grid(row=1, column=2, padx=2, pady=2)

		tkinter.Label(self.graph_settings, text='Graph Colors:').grid(row=2, column=1, padx=2, pady=2)
		self.graph_colors = tkinter.ttk.Entry(self.graph_settings)
		self.graph_colors.insert(0, settings['graph_colors'])
		self.graph_colors.grid(row=2, column=2, padx=2, pady=2)

		self.indv_board_settings = tkinter.ttk.LabelFrame(self.subroot, text='Individual Score Search')
		self.indv_board_settings.grid(row=4, column=1, columnspan=4, sticky=tkinter.EW, padx=4, pady=4, ipadx=4, ipady=4)

		tkinter.Label(self.indv_board_settings, text='Show Individual Score Search:').grid(row=1, column=1, padx=2, pady=2)
		self.indv_board_toggle = tkinter.IntVar(value=settings['indv_board'])
		self.show_graph = tkinter.ttk.Checkbutton(self.indv_board_settings, variable=self.indv_board_toggle)
		self.show_graph.grid(row=1, column=2, padx=2, pady=2)

		ok = tkinter.ttk.Button(self.subroot, text='OK', command=lambda: self.update(connection))
		# ok.bind('<Return>', lambda event: self.update(connection))
		# ok.bind('<Enter>', lambda event: self.update(connection))
		ok.grid(row=10, column=1, columnspan=4, padx=4, pady=4)

		self.subroot.focus_set()

	def import_sets(self, connection):
		location = tkinter.filedialog.askopenfilename()
		print(location)
		try:
			connection.execute("ATTACH '%s' AS OTHER;" % (location,))
			connection.execute('DELETE FROM SETTINGS;')
			connection.execute('INSERT INTO SETTINGS SELECT * FROM OTHER.SETTINGS')
			connection.commit()
			tkinter.messagebox.showinfo('Changes Made',
										'The changes have been made.\nPlease restart the application for the changes to take effect.')

		except sqlite3.OperationalError:
			tkinter.messagebox.showerror('File Error', 'The location of file you have given is either corrupt\n'
													   'or not a valid Fun Marathon file.')

	def update(self, connection):
		connection.execute('''UPDATE SETTINGS SET
							THEME = ?,
							GRAPH = ?,
							GRAPH_COLORS = ?,
							MAINBOARD_LABEL = ?,
							LEADERBOARD_LABEL = ?,
							NUM_OF_RANKS = ?,
							INDV_BOARD = ?,
							STRIPE_COLOR1 = ?,
							STRIPE_COLOR2 = ?,
							SCORE_UPDATION_DURATION = ?;''',

						   ('vista',
							self.graph_toggle.get(),
							self.graph_colors.get(),
							self.main_board_label.get(),
							self.main_board_total_scores_label.get(),
							self.num_of_ranks.get(),
							self.indv_board_toggle.get(),
							str(self.stripe1.cget('background')),
							str(self.stripe2.cget('background')),
							self.score_updation_duration.get()))
		connection.commit()
		self.subroot.destroy()
		tkinter.messagebox.showinfo('Changes Made',
									'The changes have been made.\nPlease restart the application for the changes to take effect.')

	def choose_color(self, widget):
		color = tkinter.colorchooser.askcolor(parent=self.subroot)
		widget.config(background=color[-1])
