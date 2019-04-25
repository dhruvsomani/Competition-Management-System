import sqlite3

def sanitize(file, database):
    file = open(file)

    players = file.read()
    players = players.split('\n')
    for row in range(len(players)):
        players[row] = players[row].split('\t')
        players[row][0] = int(players[row][0])

    connection = sqlite3.connect(database)
    print(players)
    for player in players:
        try:
            connection.execute('INSERT INTO PLAYERS (ID, NAME, GENDER, CATEGORY) VALUES(?, ?, ?, ?)', player)
            connection.commit()
        except:
            pass
        print(player[0])
    connection.commit()

sanitize('D:\\data.txt', 'D:\\fun_marathon.fun_marathon')