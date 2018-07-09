from os import system
import requests
import json
import re
import schedule
import time
from datetime import datetime, time
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
    speak(phrase)


def ok_to_speak():

    now = datetime.now()

    if now.weekday() > 4:
        log('Its the freaking weekend baby, have me some fun')
        return False

    if (now.time() > time(10, 1)) and (now.time() < time(10, 30)):
        log('Stand up if you love your job')
        return False

    if (now.time() > time(17, 00)) or (now.time() < time(7, 00)):
        log('ZZZZZZZZZZZ')
        return False

    return True


def speak(phrase):
    # remove any double danglers (we'll add them when we 'say' the phrase)
    phrase = re.sub('["]', '', phrase)

    if ok_to_speak():
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
    else:
       sys.stdout.write(text + "\r")
    sys.stdout.flush()

def stand_up():
    log('Stand up toot toot toot', False)
    speak('Stand up toot toot toot')


def bed_time():
    log("ZZZZZZZZZZZ", False)
    speak("That's enough for today, I'm outta here!")


def weekendybobs():
    log("It's the freakin weekend baby, have me some fun", False)
    speak("It's the freakin weekend baby, have me some fun")


def russ():
    log('Take your pills Russ', False)
    speak("Russ, have you taken your pills?")


schedule.every(2).seconds.do(run_on_start)
schedule.every(180).seconds.do(job)
schedule.every(299).seconds.do(check_for_new_phrases)
schedule.every().friday.at("18:00").do(weekendybobs)
schedule.every().day.at("10:00").do(stand_up)
schedule.every().day.at("08:30").do(russ)
schedule.every().day.at("18:30").do(bed_time)

while True:
    schedule.run_pending()
