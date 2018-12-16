#    -*- encoding: utf-8 -*-
import cPickle
import csv
import difflib
import itertools
import json
import math
import nltk
import numpy
import os
import random
import re
import time


from cPickle import (
    dump as pickle_dump,
    load as pickle_load
)

from collections import (
    Counter,
    defaultdict as deft
)

from copy import deepcopy as cp

from nltk import (
    ngrams,
    sent_tokenize as splitter,
    wordpunct_tokenize as tokenizer
)


def average(values):
    if not values:
        return None
    else:
        return sum(values) / len(values)


def prod(items):
    if not items:
        return 0.0
    r = items[0]
    for x in items[1:]:
        r *= x
    return r


def from_csv(path, delimiter=','):
    rows = []
    with open(path, 'rb') as rd:
        rdr = csv.reader(rd, delimiter=delimiter)
        for row in rdr:
            rows.append(row)
    return rows


def from_json(path):
    with open(path, 'rd') as rd:
        data = json.load(rd)
    return data


def to_json(data, path, indent=None):
    with open(path, 'wb') as wrt:
        if indent:
            json.dump(data, wrt, indent=indent)
        else:
            json.dump(data, wrt)


def timestamp():
    month, day, hh, mm, ss = time.localtime()[1:6]
    return '%d-%d %d.%d.%d' % (day, month, hh, mm, ss)


def trimstring(string):
    start, end = 0, len(string)
    for i, char in enumerate(string):
        if DATA.match(char):
            start = i
            break
    for i in range(len(string)):
        j = -(i + 1)
        char = string[j]
        if DATA.match(char):
            break
    end += j + 1
    return string[start:end]


def read(path):
    txt = ''
    with open(path, 'r') as wrt:
        for l in wrt:
            txt += l
    return decode(txt)


def readlines(path):
    ll = []
    with open(path, 'r') as wrt:
        for l in wrt:
            ll.append(l)
    return [decode(l) for l in ll]


def words(string):
    ww = []
    for w in tokenizer(string):
        ww.append(w.lower())
    return ww


def encode(string):
    try:
        return string.encode('utf-8')
    except Exception:
        return string


def decode(string):
    try:
        return string.decode('utf-8')
    except Exception:
        return string


def to_csv(rows, path, delimiter=None):
    with open(path, 'wb') as wrt:
        if delimiter:
            wrtr = csv.writer(wrt, quoting=csv.QUOTE_MINIMAL, delimiter=delimiter)
        else:
            wrtr = csv.writer(wrt, quoting=csv.QUOTE_MINIMAL)
        for row in rows:
            wrtr.writerow(row)

def pyclean():
    cmd = 'rm *.pyc'
    os.system(cmd)


def to_pickle(data, path):
    with open(path, 'wb') as wrt:
        pickle_dump(data, wrt)


def from_pickle(path):
    with open(path, 'rd') as rd:
        data = pickle_load(rd)
    return data


def get_files(folder):
    return ['%s/%s' % (folder, f) for f in os.listdir(folder)]

