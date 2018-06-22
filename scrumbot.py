from os import system
import requests
import json
import re
import schedule
import time
from datetime import datetime
import random
import sys

class Phrases(list):
    def add_new_phrase(self, phrase):
        self.append(phrase)

    def remove_old_phrase(self, text):
        for i, phrase in enumerate(self):
            if phrase.phrase == text:
                del(self[i])
                break

    def phrase_count(self):
        return len(self)

    def phrases_remaining(self):
        if len(self) == 0:
            return False
        else:
            for phrase in self:
                if phrase.used is False:
                    return True
        return False

    def get_random_phrase(self):
        random_list = []
        for phrase in self:
            if phrase.used is False:
                random_list.append(phrase)

        random.shuffle(random_list)
        selected = random_list.pop()
        self.update_phrase(selected.phrase)
        return selected.phrase

    def update_phrase(self, phrase_to_update):
        for phrase in self:
            if phrase.phrase == phrase_to_update:
                phrase.used = True
                return

    def reset_list(self):
        for phrase in self:
            phrase.used = False

    def as_set(self):
        phrases_set = set()
        for phrase in self:
            phrases_set.add(phrase.phrase)

        return phrases_set


class Phrase(object):
    def __init__(self, phrase, used=False):
        self.phrase = phrase
        self.used = used


phrases_list = Phrases()


def job():
    global phrases_list

    if phrases_list.phrases_remaining() == False:
        print('Restarting phrases - ' + str(datetime.now()))
        phrases_list.reset_list()

    # randomly shuffle the list before picking the one to say
    phrase = phrases_list.get_random_phrase()

    # remove any double danglers (we'll add them when we 'say' the phrase)
    phrase = re.sub('["]', '', phrase)

    log(phrase, True)

    # say the phrase (double danglers allow for punctuation)
    system('say {}'.format('"' + phrase + '"'))

def run_on_start():
    global phrases_list

    print('Job started at - ' + str(datetime.now()))
    file_phrases_list = read_phrases_from_file()
    for text in file_phrases_list:
        new_phrase = Phrase(text)
        phrases_list.add_new_phrase(new_phrase)
    job()
    return schedule.CancelJob

def call_git():
    # call the gist to return the latest phrases
    log('requesting phrases')
    url = 'https://api.github.com/gists/f37d184552dd58ee835d8c281ea333f1'
    r = requests.get(url)
    phrases_json = json.loads(r.text)
    phrases = phrases_json['files']['scrumbot_phrases.txt']['content']
    return phrases.splitlines()

def read_phrases_from_file():
    log('reading phrases from file')
    with open('scrumbot_phrases.txt') as f:
        return f.read().splitlines()

def check_for_new_phrases():
    # update the master phrase list and add new phrases to the working list
    global phrases_list
    log('check new phrases')
    git_phrases_list = read_phrases_from_file()
    phrases_set = phrases_list.as_set()
    to_add = list(set(git_phrases_list) - phrases_set)
    to_remove = list(phrases_set - set(git_phrases_list))

    for text in to_add:
        new_phrase = Phrase(text)
        phrases_list.add_new_phrase(new_phrase)

    for old_phrase in to_remove:
        phrases_list.remove_old_phrase(old_phrase)

def log(text, is_phrase=False):
    sys.stdout.write("\033[K")
    if is_phrase:
        sys.stdout.write("Last phrase read was - " + text + "\r")
        # sys.stdout.write("Last phrase read was - " + text + "\n")
    else:
       sys.stdout.write(text + "\r")
    #    sys.stdout.write(text + "\n")
    sys.stdout.flush()

def stand_up():
    log("Stand up toot toot toot " + str(datetime.now()))
    system('say {}'.format('Stand up toot toot toot'))
    # sleep for 30 mins (1800 seconds)
    time.sleep(1800)


def bed_time():
    # Turn off between 6pm and 7am (46800 seconds)
    log("Going to bed now " + str(datetime.now()))
    system('say {}'.format("That's enough for today, I'm outta here!"))
    # sleep 13 hours 6pm to 7am
    for x in range(780):
        log(str(x))
        time.sleep(60)
    log('yawn')


def weekendybobs():
    # Turn off between 6pm Friday and 7am Monday(219600 seconds)
    log("Time to party! Weekendybobs " + str(datetime.now()))
    system('say {}'.format("It's Friday baby, time to party!"))
    # sleep 61 hours fri 6pm - mon 7am
    time.sleep(219600)


def russ():
    # Turn off between 6pm Friday and 7am Monday(219600 seconds)
    log("Remind Russ" + str(datetime.now()))
    system('say {}'.format("Russ, have you taken your pills?"))


schedule.every(2).seconds.do(run_on_start)
schedule.every(180).seconds.do(job)
schedule.every(299).seconds.do(check_for_new_phrases)
schedule.every().friday.at("18:00").do(weekendybobs)
schedule.every().day.at("10:00").do(stand_up)
schedule.every().day.at("08:30").do(russ)
schedule.every().day.at("18:00").do(bed_time)

while True:
    schedule.run_pending()
    # time.sleep(2)
