# coding: utf-8
__metaclass__ = type

class BaseClass():
    """description of class"""
    STATE_OK = 1
    STATE_ERROR = -1

    def __init__(self):
        self.state = 'ok'
    
    def ok(self):
        self.state = 'ok'
        return BaseClass.STATE_OK

    def error(self, err_msg=None):
        if err_msg:
            self.state = err_msg
        return BaseClass.STATE_ERROR