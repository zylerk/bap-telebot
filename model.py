# coding: utf-8

# standard app engine imports
from google.appengine.ext import ndb

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=True, default=False)
    classification = ndb.IntegerProperty(default = 1)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.classification = 1
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def getClass(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es.classification:
        return es.classification
    else:
        es.classification = 1
        es.put()
        return es.classification

    return -1

def get_enabled_chats():
    # get_enabled: 봇이 활성화된 채팅 리스트 반환
    # return: (list of EnableStatus)
    #
    query = EnableStatus.query(EnableStatus.enabled == True)
    return query.fetch()

def get_all_user():
    query = EnableStatus.query()
    return query.fetch()
