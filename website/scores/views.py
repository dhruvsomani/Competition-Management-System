from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import Template, Context, RequestContext
from django.http import JsonResponse
import sqlite3
import bisect


def process_name(string):
    return 'game_' + string.replace(' ', '_').replace("'", '').replace('"', '')


def list_games(request):
    database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')
    file = Template(open('scores\\list.html').read())

    games_list = list(map(lambda x: x.__getitem__(0), database.execute('SELECT NAME FROM GAMES;')))

    context = Context({'games_list': tuple(games_list)})

    return HttpResponse(file.render(context))


def manage(request, game_name=None):
    database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')
    file = Template(open('scores\\manage2.html').read())

    if game_name is None:
        games_list = list(map(lambda x: x.__getitem__(0), database.execute('SELECT NAME FROM GAMES;')))

        context = RequestContext(request, {'games_list': tuple(games_list), })

    else:
        context = RequestContext(request, {'games_list': (game_name,),
                                           'game': game_name})

    return HttpResponse(file.render(context))


def update(request, game_name=None):
    if 'id' in request.POST and 'score' in request.POST and 'game' in request.POST and 0 <= float(request.POST['score'])\
            and float(request.POST['score']) <= 10:

        database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')

        database.execute('UPDATE PLAYERS SET %s = %s WHERE ID = %s;' % (process_name(request.POST['game']),
                                                                        request.POST['score'],
                                                                        request.POST['id']))
        database.commit()

        return HttpResponseRedirect('../' + 'game/' + request.POST['game'])

    else:
        return HttpResponse('Failed!')


def player_data(request, player_id=None, game=None):
    if player_id is None:
        player_id = request.POST['id']
    if game is None:
        game = request.POST['game']

    database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')

    games = list(database.execute('SELECT NAME FROM GAMES;'))

    data = list(database.execute('SELECT ID, NAME, %s FROM PLAYERS WHERE ID = %s' % (process_name(game), player_id)))[0]

    details = dict()
    details['id'] = data[0]
    details['name'] = data[1]
    details['prev_score'] = data[2]

    # for index in range(len(games)):
    #     details[games[index][0]] = data[index+2]

    return JsonResponse(details)


def gameboard(request, game_name=None) :
    database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')
    file = Template(open('scores\\gameboard.html').read())

    columns = []
    games_played = []

    for item in database.execute('SELECT NAME FROM GAMES;').fetchall():
        columns.append('COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)')
        games_played.append('(CASE WHEN %s IS NULL THEN 0 ELSE 1 END)' % (process_name(item.__getitem__(0))))

    columns = ' + '.join(columns)
    games_played = ' + '.join(games_played)

    leader_data = list(database.execute('SELECT ID, NAME, %s, %s FROM PLAYERS WHERE %s IS NOT NULL ORDER BY %s DESC, %s DESC;' %
                                        (process_name(game_name), columns, process_name(game_name), process_name(game_name), columns)))

    scores = [-item[2] for item in leader_data]
    scores.sort()

    for i in range(len(leader_data)):
        leader_data[i] = list(leader_data[i])
        leader_data[i].append(bisect.bisect_left(scores, -leader_data[i][2]) + 1)

    context = Context({'game': game_name,
                        'leader_list': leader_data})

    return HttpResponse(file.render(context))


def leaderboard(request):
    database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')
    file = Template(open('scores\\leaderboard.html').read())

    columns = []
    games_played = []

    for item in database.execute('SELECT NAME FROM GAMES;').fetchall():
        columns.append('COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)')
        games_played.append('(CASE WHEN %s IS NULL THEN 0 ELSE 1 END)' % (process_name(item.__getitem__(0))))

    columns = ' + '.join(columns)
    games_played = ' + '.join(games_played)

    leader_data = list(database.execute('SELECT ID, NAME, %s, %s FROM PLAYERS WHERE %s > 0 ORDER BY %s DESC, %s ASC;' %
                                        (columns, games_played, games_played, columns, games_played)))

    scores = [-item[2] for item in leader_data]
    scores.sort()

    for i in range(len(leader_data)):
        leader_data[i] = list(leader_data[i])
        leader_data[i].append(bisect.bisect_left(scores, -leader_data[i][2]) + 1)

    context = Context({'leader_list': leader_data})

    return HttpResponse(file.render(context))


def coupleboard(request):
    database = sqlite3.connect('F:\\Programming\\Fun Marathon\\final.fun_marathon')
    file = Template(open('scores\\coupleboard.html').read())

    couples = open('F:\\Programming\\Fun Marathon\\couples.txt').read()
    couples = couples.split('\n')
    couples.pop()

    couples = [item for item in couples if item.strip('\t').strip() != '']

    for i in range(len(couples)):
        couples[i] = couples[i].split('\t')
        couples[i][0] = int(couples[i][0])
        couples[i][1] = int(couples[i][1])

    columns = []
    games_played = []

    for item in database.execute('SELECT NAME FROM GAMES;').fetchall():
        columns.append('COALESCE(' + process_name(item.__getitem__(0)).upper() + ', 0)')
        games_played.append('(CASE WHEN %s IS NULL THEN 0 ELSE 1 END)' % (process_name(item.__getitem__(0))))

    columns = ' + '.join(columns)
    games_played = ' + '.join(games_played)

    leader_data = list(database.execute('SELECT ID, NAME, %s, %s FROM PLAYERS ORDER BY ID;' %
                                        (columns, games_played)))

    dictionary = dict()
    for player in leader_data:
        dictionary[player[0]] = player[1:]

    couple_leaderboard = []
    for couple in couples:
        couple_leaderboard.append([dictionary[couple[0]][1] + dictionary[couple[1]][1], dictionary[couple[0]], dictionary[couple[1]], couple])
    couple_leaderboard.sort(reverse=True)

    scores = [-item[0] for item in couple_leaderboard]
    scores.sort()

    for i in range(len(couple_leaderboard)):
        couple_leaderboard[i] = list(couple_leaderboard[i])
        couple_leaderboard[i].append(bisect.bisect_left(scores, -couple_leaderboard[i][0]) + 1)

    couple_leaderboard = [item for item in couple_leaderboard if (item[0] != 0)]

    final = []
    for row in couple_leaderboard:
        final.append([row[3][0], row[3][1], row[1][0] + ' - & - ' + row[2][0], row[1][1], row[2][1], row[0], row[4]])

    context = Context({'couple_list': final})

    return HttpResponse(file.render(context))


def bootstrap(request):
    response = HttpResponse(open('scores\\bootstrap.min.css').read(), )
    response['Content-Type'] = 'text/css'
    return response


def javascript(request):
    response = HttpResponse(open('scores\\bootstrap.min.js').read(), )
    response['Content-Type'] = 'text/js'
    return response

def jquery(request):
    response = HttpResponse(open('scores\\jquery.min.js').read(), )
    response['Content-Type'] = 'text/js'
    return response