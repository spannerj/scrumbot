from os import system
import requests
import json
import re
import schedule
import time
from datetime import datetime

phrases_list = []


print('Job started at - ' + str(datetime.now()))

def job():
    global phrases_list

    if len(phrases_list) == 0:
        print('calling git')
        url = 'https://api.github.com/gists/f37d184552dd58ee835d8c281ea333f1'
        r = requests.get(url)
        phrases_json = json.loads(r.text)
        phrases = phrases_json['files']['scrumbot_phrases.txt']['content']
        phrases_list = phrases.splitlines()

    phrases_set = set(phrases_list)
    print(phrases_set)
    print(type(phrases_set))

    import random
    random.shuffle(phrases_list)
    phr = phrases_list.pop()
    print(phr)
    print(phrases_list)
    # rem = random.choice(list(phrases_set))
    # print(rem)
    # phrases_set = phrases_set.remove(rem)

    for phrase in phrases_list:
        print("I just read - {}".format(phrase))
        phrase = re.sub('["]', '', phrase)
        system('say {}'.format('"' + phrase + '"'))

def stand_up():
    print("Stand up toot toot toot " + str(datetime.now()))
    system('say {}'.format('Stand up toot toot toot'))
    time.sleep(1)
    # time.sleep(1800)

def bed_time():
    print("Going to bed now " + str(datetime.now()))
    # sleep 13 hours 6pm to 7am
    time.sleep(46800)

def weekendybobs():
    print("Time to party! Weekendybobs " + str(datetime.now()))
    # sleep 61 hours fri 6pm - mon 7am
    time.sleep(219600)

schedule.every(5).seconds.do(job)
# schedule.every().friday.at("18:00").do(weekendybobs)
# schedule.every().day.at("10:00").do(stand_up)
# schedule.every().day.at("18:00").do(bed_time)

schedule.every().friday.at("17:33").do(weekendybobs)
schedule.every().day.at("17:32").do(stand_up)
schedule.every().day.at("17:33").do(bed_time)

while True:
    
    schedule.run_pending()
    time.sleep(1)