import requests
import time
import datetime

url = 'http://dhruvsomani.pythonanywhere.com/scores/database'
path = 'F:\\Programming\\Fun Marathon\\final.fun_marathon'

while True:
        try:
            print(datetime.datetime.now(),
                    requests.post(url, files={'database': ('final', open(path, 'rb'), 'text')}))
        except Exception as e:
            print(e)

        time.sleep(30)
