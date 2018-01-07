# coding: utf-8

import datetime
from model import *
from BapDB import BapDB

def process_msg(text, chat_id=None):

    text = text.lower()

    if 'who' in text:
        return 1, u'I am Bitoin Trade Bot'

    elif 'time' in text or u'시간' in text:
        time_utc = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
        time_seoul = datetime.datetime.now() + datetime.timedelta(hours=9)
        time_seoul = time_seoul.replace(microsecond=0).isoformat(' ')
        time_result = u'utc = {0} \n 서울 = {1}'.format(time_utc, time_seoul)
        return 1, time_result

    elif 'btc' in text or u'비트' in text:
        db = BapDB()
        return  db.getInfo('btc')

    elif 'eth' in text or u'이더' in text:
        db = BapDB()
        return db.getInfo('eth')

    elif 'xrp' in text or u'리플' in text:
        db = BapDB()
        return db.getInfo('xrp')

    elif 'all' in text or u'모두' in text:
        db = BapDB()
        return db.getAll()

    elif 'user' in text or u'사용자' in text:
        r_str = u'사용자 리스트 \n'

        for chat in get_all_user():
            r_str += chat.key.string_id() + u'\n'

        return 1, r_str

    return -1, ''

