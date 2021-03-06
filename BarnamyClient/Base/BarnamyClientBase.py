# -*- coding: utf-8 -*-

from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from streaming_schema import BarnamyClientSchema
from Settings.BarnamySettings import BarnamySettings as BRS
from PasteBin.barnamyPasteBin import BarnamayPastBin as BRP
from Log.BarnamyLog import BarnamyLog as BRL
from time import gmtime, strftime
import subprocess
import msgpack
import GUI
import Audio
import Notify
import os
import signal
import getpass
from os.path import expanduser
import random
import string

BARNAMY_HOME = expanduser("~/BarnamyHome")
BARNAMY_HTTP_PASSWD_FILE = expanduser("~/.barnamy/httpd.password")
USER = getpass.getuser()

class BarnamyClient(LineReceiver):
    def connectionMade(self):
        self.packer = msgpack.Packer()
        self.unpacker = msgpack.Unpacker()
        self.schema = BarnamyClientSchema()
        self.barnamy_log = BRL()
        self.barnamy_setting_i = BRS()
        self.token_id = None
        self.nick = None
        self._pid = None
        self.barnamy_cmd = {'/admin' : 'for sending message to Admin', '/ignore' : 'to ignore user',
        '/unignore' : 'to unignore user', '/run_srv':'Run barnamy server', '/stop_srv':'Stop barnamy server'}

        self.barnamy_settings_actions = {'save_settings' : self.save_settings, 'get_settings' : self.get_settings}

        self.barnamy_sound_setting = {'send_prv_msg_sound' : self.send_prv_msg_sound, 'login_sound' : self.login_sound,
         'logout_sound' : self.logout_sound, 'received_prv_msg_sound' : self.received_prv_msg_sound, 
         'access_folder_sound' : self.access_folder_sound}

        self.barnamy_actions = {'send_pub_msg' : self.send_pub_msg, 'send_prv_msg' : self.send_prv_msg, 'do_login': self.do_login,
         'do_logout' : self.do_logout, 'ask_for_folder_access' : self.ask_for_folder_access, 'regiser_new_user' : self.regiser_new_user,
         '_notify' : self._notify, '_log' : self._log, 'start_web_server' : self.start_web_server, 'stop_web_server':self.stop_web_server
         ,'accept_share' : self.accept_share, 'ignore_user': self.ignore_user, 'unignore_user': self.unignore_user}

        self.barnamy_status = {'online' : self.go_online, 'away' : self.go_away}
        self.BarnamyPlayer = Audio.BarnamyAudio.BarnamyAudio()
        self.BarnamyNotify = Notify.BarnamyNotify.BarnamyNotify()
        self.app = GUI.BarnamyClientGui.BarnamyClientGui(self)
        self.app.RunBarnamyLogin()

    def regiser_new_user(self, data):
        self.sendLine(self.packer.pack(data))

    def do_login(self, data):
        self.sendLine(self.packer.pack(data))

    def do_logout(self, data):
        self.sendLine(self.packer.pack(data))
        self.barnamy_sound_setting['logout_sound']()

    def ask_for_folder_access(self, data):
        self.sendLine(self.packer.pack(data))

    def send_pub_msg(self, data):
        if self.barnamy_setting_i.get_settings()['log']:
            self.barnamy_log.set_log("barnamy_public_%s" %data['nick'] , "[%s]<%s>%s\n" %(strftime("%H:%M:%S", gmtime()), 
                data['nick'], data['msg']))
        self.sendLine(self.packer.pack(data))

    def login_sound(self):
        if self.barnamy_setting_i.get_settings()['sound']:
            self.BarnamyPlayer.login_sound()

    def received_prv_msg_sound(self):
        if self.barnamy_setting_i.get_settings()['sound']:
            self.BarnamyPlayer.receive_msg_sound()

    def logout_sound(self):
        if self.barnamy_setting_i.get_settings()['sound']:
            self.BarnamyPlayer.logout_sound()

    def access_folder_sound(self):
        if self.barnamy_setting_i.get_settings()['sound']:
            self.BarnamyPlayer.access_folder_sound()

    def go_online(self, data):
        self.sendLine(self.packer.pack(data))

    def go_away(self, data):
        self.sendLine(self.packer.pack(data))

    def send_prv_msg(self, data):
        if self.barnamy_setting_i.get_settings()['log']:
            self.barnamy_log.set_log("barnamy_prv_%s_%s"%(data['from_'] , data['to_']), "[%s]<%s>%s\n" %(strftime("%H:%M:%S", gmtime()), 
                data['from_'], data['to_']))

        self.barnamy_sound_setting['send_prv_msg_sound']()
        self.sendLine(self.packer.pack(data))

    def send_prv_msg_sound(self):
        if self.barnamy_setting_i.get_settings()['sound']:
            self.BarnamyPlayer.send_msg_sound()

    def send_paste_bin(self, data):
        self.sendLine(self.packer.pack(data))

    def _notify(self, data1, data2):
        if self.barnamy_setting_i.get_settings()['notify']:
            self.BarnamyNotify.show_notify(data1, data2)

    def save_settings(self, data):
        self.barnamy_setting_i.save_settings(data)

    def get_settings(self):
        settings = self.barnamy_setting_i.get_settings()
        return settings

    def _log(self, data):
        if self.barnamy_setting_i.get_settings()['log']:
            self.barnamy_log.set_log(data[0], data[1])

    def lineReceived(self, data):
        self.unpacker.feed(data)
        data = self.unpacker.unpack()
        if self.schema.status_schema_f(data): self.app.recv_status_before_connexion(data)

        if self.schema.status_schema_user_f(data): self.app.recv_status_user(data)

        if self.schema.login_nok_schema_f(data): self.app.recv_login_nok(data)

        if self.schema.error_schema_f(data): self.app.recv_error_schema(data)

        if self.schema.user_join_left_schema_f(data):
            self.app.recv_user_join_left(data)
            self.barnamy_actions['_notify']("Barnamy", data['user_join_left'])

        if self.schema.access_folder_schema_f(data):
            self.app.recv_access_folder(data)
            self.barnamy_sound_setting['access_folder_sound']()

        if self.schema.access_folder_valid_schema_f(data):
            self.app.recv_access_folder_valid(data)

        if self.schema.login_schema_f(data):
            self.token_id = data["token_id"]
            self.nick = data["nick"]
            self.app.recv_login_users(data)
            self.barnamy_sound_setting['login_sound']()

        if self.schema.register_schema_f(data): self.app.recv_register(data)

        if self.schema.public_message_f(data): self.app.recv_public_msg(data)

        if self.schema.private_message_f(data):
            self.app.recv_prv_msg(data)
            self.barnamy_sound_setting['received_prv_msg_sound']()
            self.barnamy_actions['_notify']( data['from_'], data['msg'])

    def pastebin(self, data):
        if data[0] == "paste.scsys":
            url = BRP.fpaste_scsys(data[1], data[2], data[3])
        elif data[0] == "bpaste":
            url = BRP.bpaste(data[1])
        return url

    def start_web_server(self):
        try:
            self._pid = subprocess.check_output(['pgrep', 'twistd', '-u', USER])
            return False
        except subprocess.CalledProcessError:
            self._pid = subprocess.Popen(['twistd', '-n', 'web', '--resource-script', 'Base/MiniShareServer/EngineShareServer.rpy', '--port', '%s'%self.get_settings()['wport']]) #start
            return True

    def stop_web_server(self):
        if self._pid:
            os.kill(self._pid.pid, signal.SIGKILL)
            self._pid = None

    def accept_share(self, nick):
        passwd = None
        passwd_f = open(BARNAMY_HTTP_PASSWD_FILE, 'r')
        exist = False
        for passwd_l in passwd_f:
            if passwd_l.split(':')[0] == nick:
                exist = True
                passwd = passwd_l.split(':')[1]
                break

        if not exist:
            BARNAMY_HOME_NICK = "%s/%s" %(BARNAMY_HOME, nick)
            if not os.path.exists(BARNAMY_HOME_NICK):
                os.makedirs(BARNAMY_HOME_NICK)
            passwd_f = open(BARNAMY_HTTP_PASSWD_FILE, 'a')
            passwd = ''.join(random.choice(string.ascii_uppercase + string.digits + string.lowercase) for _ in range(7))
            passwd_f.write("%s:%s\n"%(nick, passwd))
            passwd_f.close()
        data = {'type':'access_folder_valid', 'from_':self.nick, 'to_':nick, 'passwd':passwd, 'token_id':self.token_id}
        self.sendLine(self.packer.pack(data))

    def ignore_user(self, nick):
        data = {'type':'ignore', 'nick':nick, 'token_id':self.token_id}
        self.sendLine(self.packer.pack(data))

    def unignore_user(self, nick):
        data = {'type':'unignore', 'nick':nick, 'token_id':self.token_id}
        self.sendLine(self.packer.pack(data))

class BarnamyClientFactory(ClientFactory):
    protocol = BarnamyClient

    def __init__(self):
        self.done = Deferred()

    def clientConnectionFailed(self, connector, reason):
        print('connection failed:', reason.getErrorMessage())
        self.done.errback(reason)

    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
        self.done.callback(None)
