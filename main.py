import sys

from bs4 import BeautifulSoup
import requests

from datetime import timedelta

import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.58 Safari/537.36'}

showlist = []

totalTime = timedelta()

def getShows(userId):
    global showlist
    global totalTime
    url = f'https://www.tvtime.com/en/user/{userId}/profile'
    req = requests.get(url, headers=headers)
    html_text = req.text

    soup = BeautifulSoup(html_text, 'lxml')

    allShows = soup.find('div', id='all-shows')

    try: 
        showCards = allShows.find_all('li', class_='first-loaded')

        for show in showCards:
            details = show.find('div', class_='poster-details')

            showDetail = {
                'name': details.h2.a.text.strip(),
                'duration_watched': details.h3.text.strip(),
            }
            showlist.append(showDetail)

            duration = showDetail['duration_watched'].split()
            months = 0
            days = 0
            hours = 0
            minutes = 0
            if 'minutes' in duration: minutes = int(duration[-2])
            if 'days' in duration: days = int(duration[0])
            if 'hours' in duration and 'days' in duration: hours = int(duration[2])
            else: hours = int(duration[0])

            totalTime += timedelta(days=days, hours=hours, minutes=minutes)

        months = 0
        if totalTime.days > 30: 
            months = totalTime.days//30
            totalTime -= timedelta(days=months*30)

        totalTimeStr = f'{months} months {totalTime.days} days {totalTime.seconds//3600} hours {(totalTime.seconds//60)%60} minutes'
        
        print(f'total time watched: {totalTimeStr}')

        showlist.append({
            'name': '##Totale Time##',
            'duration_watched': totalTimeStr,
        })

        if param == '-e':
            df = pd.DataFrame(showlist)
            df.to_excel(f'stackshows_{userId}.xlsx')
            print("xl file generated.")
    except AttributeError:
        print("This profile is private.")

if __name__ == '__main__':
    args = sys.argv
    param = ''
    if len(args) == 2:
        userId = args[1]
    elif len(args) == 3:
        userId, param = args[1:]
    else:
        print("wrong number of arguments")
        exit()
        
    getShows(userId)