"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    # http://192.168.0.208:8000/scores/
    url(r'^$', views.list_games, name='list_games'),

    #
    url(r'^leaderboard/?$', views.leaderboard, name='Leaderboard'),

    #
    url(r'^leaderboard/(?P<game_name>[^/]+)/?$', views.gameboard, name='gameboard'),

    #
    url(r'^coupleboard/?$', views.coupleboard, name='Coupleboard'),

    # http://192.168.0.208:8000/scores/update/?game=Shoot_the_Balls&id=27&score=5
    url(r'^update/$', views.update, name='update'),

    # http://192.168.0.208:8000/scores/player_data/
    url(r'^player_data/$', views.player_data, name='player_data'),

    # http://192.168.0.208:8000/scores/player_data/101/
    url(r'^player_data/(?P<player_id>[^/]+)/$', views.player_data, name='player_data'),

    # http://192.168.0.208:8000/scores/game/<game_name>/
    url(r'^game/(?P<game_name>[^/]+)/?$', views.manage, name='index'),

    # http://192.168.0.208:8000/scores/game/<game_name>/update/
    url(r'^game/(?P<game_name>[^/]+)/update/$', views.update, name='update_game'),

    # http://192.168.0.208:8000/scores/bootstrap.min.css
    url(r'^bootstrap.min.css', views.bootstrap, name='bootstrap'),

    # http://192.168.0.208:8000/scores/bootstrap.min.js
    url(r'^bootstrap.min.js', views.javascript, name='javascript'),

    #
    url(r'^jquery.min.js', views.jquery, name='jquery')
]
