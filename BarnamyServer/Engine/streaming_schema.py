# -*- coding: utf-8 -*-

from schema import Schema, And, Use

class BarnamyServerSchema(object):
    
    def __init__(self):
        self.login_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'login'),
                                       'nick': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'passwd':And(str)})
        self.register_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'register'),
                                       'nick': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'passwd':And(str), 'email':And(str, Use(str.lower))})
        self.msg_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'public'),
                                       'nick': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'token_id':And(str), 'msg':And(str)})
        self.prv_msg_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'private'),
                                       'to_':And(str), 'from_': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'token_id':And(str), 'msg':And(str)})

        self.logout_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'logout'),
                                       'nick': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'token_id':And(str)})

        self.access_folder_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'folder'),
                                       'to_':And(str), 'from_': And(str),
                                       'token_id':And(str)})

        self.status_schema = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'status'),
                                       'nick': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'token_id':And(str), 'status':And(str)})

        self.msg_admin = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'admin'),
                                       'nick': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'token_id':And(str), 'msg':And(str)})

        self.access_folder_valid = Schema({'type' : And(str, Use(str.lower), lambda n: n == 'access_folder_valid'),
                                       'from_': And(str, Use(str.lower), lambda n: 4 <= len(n) <= 10),
                                       'to_':And(str), 'passwd':And(str), 'token_id':And(str)})

        self.error = {"login_syntax" : '{"type":"login", "nick":"4 <= len(str) <= 10", "passwd":"str"}',
                      "register_syntax" : '{"type":"register", "nick":"4 <= len(str) <= 10", "passwd":"str", "email":"str"}',
                      "pub_public_msg_syntax" : '{"type":"public", "nick":"4 <= len(str) <= 10", "token_id":"str", "msg":"str"}',
                      "pub_public_msg_syntax" : '{"type":"public", "nick":"4 <= len(str) <= 10", "token_id":"str", "msg":"str"}'}
    
    def login_schema_f(self, data):
        try:
            data = self.login_schema.validate(data)
            return True
        except Exception:
            return False

    def msg_admin_f(self, data):
        try:
            data = self.msg_admin.validate(data)
            return True
        except Exception:
            return False

    def access_folder_valid_f(self, data):
        try:
            data = self.access_folder_valid.validate(data)
            return True
        except Exception:
            return False

    def access_folder_f(self, data):
        try:
            data = self.access_folder_schema.validate(data)
            return True
        except Exception:
            return False
    
    def status_f(self, data):
        try:
            data = self.status_schema.validate(data)
            return True
        except Exception:
            return False   
    
    def register_schema_f(self, data):
        try:
            data = self.register_schema.validate(data)
            return True
        except Exception:
            return False
    
    def public_message_f(self, data):
        try:
            data = self.msg_schema.validate(data)
            return True
        except Exception:
            return False
    
    def private_message_f(self, data):
        try:
            data = self.prv_msg_schema.validate(data)
            return True
        except Exception:
            return False

    def logout_f(self, data):
        try:
            data = self.logout_schema.validate(data)
            return True
        except Exception:
            return False