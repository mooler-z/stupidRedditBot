#!/usr/bin/python3

import sqlite3
from sqlite3 import Error
import nltk
from pprint import pprint as pp
import time
import os

reddit = {
    "col2": "comment",
    "col1": "pcomment",
    "table": "parent_reply"
}

grading = ["N", "V", "W", "P", "J", "I"]

db = "Reddit_comments.db"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def get_pos_tag_pair(pos, arr):
    return [i for i in arr if i[1][0]==pos]


def get_auto_command(arrs):
    _sql = f"SELECT {reddit['col1']}, {reddit['col2']} FROM {reddit['table']} WHERE"
    temp = ' {} like "% {} %"'
    for i, noun in enumerate(arrs):
        if(i>0):
            _sql += " or "

        _sql += temp.format(reddit['col1'], noun[0])
    else:
        _sql += ";"

    return _sql


def get_verbed(curs, verbs):
    cleaner = [[], []]
    for i in curs.fetchall():
        bools = True
        for verb in verbs:
            if verb[0].lower() in i[0].lower():
                cleaner[1].append(i)
            else:
                bools = False
        else:
            if bools:
                cleaner[0].append(i)
    return cleaner

def get_details(the_rest, results, k):
    _results = [[], []]
    for result in results:
        bools = True
        for rest in the_rest:
            _result = [i.lower() for i in result[k].split(" ")]
            if rest[0].lower() in _result:
                _results[1].append(result)
            else:
                bools = False
        else:
            if bools:
                _results[0].append(result)
    return _results[0] if len(_results[0]) else _results[1]


def get_graded_sql(nlp):
    nouns = get_pos_tag_pair("N", nlp)
    verbs = get_pos_tag_pair("V", nlp)
    nouns = get_auto_command(nouns)
    print(nouns)
    user_input = [i[0] for i in nlp]

    the_rest = get_pos_tag_pair("W", nlp) + get_pos_tag_pair("P", nlp)\
        + get_pos_tag_pair("J", nlp) + get_pos_tag_pair("I", nlp)\
        + get_pos_tag_pair(".", nlp)

    conn = create_connection(db)

    results = None
    if(conn):
        curs = conn.cursor()
        curs.execute(nouns)
        allEm = get_verbed(curs, verbs)
        if len(allEm[0]):
            if len(allEm[0]) > 3:
                results = get_details(the_rest, allEm[0], 0)
                results = get_details(get_pos_tag_pair("N", nlp)+get_pos_tag_pair("V", nlp), results, 1)
                print("FIRST")
            else:
                return allEm[0]
        else:
            if len(allEm[1]) > 3:
                results = get_details(the_rest, allEm[1], 0)
                results = get_details(get_pos_tag_pair("N", nlp)+get_pos_tag_pair("V", nlp), results, 1)
                print("Second")
            else:
                return allEm[1]

        for result in results:
            print("Ques>> ", result[0])
            print("Ans>> ", result[1])
            print("\n--------------------\n")

    else:
        print("Error occurred when connecting to db")



def get_user_input():
    nlp = nltk.word_tokenize
    user_input = input(">> ")
    nlp = nlp(user_input)
    nlp = nltk.pos_tag(nlp)
    get_graded_sql(nlp)


if __name__ == '__main__':
    get_user_input()
