import sqlite3

def sanitize(file, database):
	file = open(file)

	players = file.read()
	players = players.split('\n')

	for i in range(len(players)):
		players[i] = players[i].split('\t')

	players.pop()

	connection = sqlite3.connect(database)
	
	for player in players:
		try:
			connection.execute('INSERT INTO PLAYERS (ID, NAME) VALUES(?, ?)', (player[0], player[1]))
			connection.commit()
		except:
			pass

		print(player[0], player[1])
	connection.commit()

sanitize('F:\\Programming\\Fun Marathon\\participants.txt', 'F:\\Programming\\Fun Marathon\\final.fun_marathon')