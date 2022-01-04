from pymodules import FileDbGroup
from telegram.ext import Updater
import pred_learn_update_dbs

bot = Updater("473980782:AAEJ3BLe9nBGv9iE_6JwUPT5j5KJB8VpfdY").bot


class Group(object):
    def __init__(self, chat_id):
        self.chat_id = str(chat_id)
        self.groups_data = FileDbGroup.FileDbGroup(self.chat_id)

    def get_good_ls(self):
        return self.groups_data.get_good_ls()

    def get_spam_ls(self):
        return self.groups_data.get_spam_ls()

    def rem_spam_from_tempgood_update_main_dbs(self, ):
        self.groups_data.rem_spam_from_tempgood_update_main_dbs()

    def get_data(self):
        return self.groups_data.get_data_of_chat()

    def update_chat_data(self, my_data):
        self.groups_data.write_new_data(my_data)

    def is_spam(self, msg, time):
        return pred_learn_update_dbs.is_spam(msg=msg, time=time, group_code=self.chat_id)

    def is_remove_activated(self):
        return self.groups_data.is_rem_activated()

    def deactivate_spam_remove(self):
        self.groups_data.deactivate_spam_remove()

    def activate_spam_remove(self):
        self.groups_data.activate_spam_remove()

    def deactivate_auto_label(self):
        self.groups_data.deactivate_auto_label()

    def activate_auto_label(self):
        self.groups_data.activate_auto_label()

    def add_new_msg(self, time, txt, label):
        if label == "0":
            self.groups_data.add_to_temp_good(time, txt)
        elif label == "1":
            self.groups_data.add_to_temp_spam(time, txt)

    def add_authorized(self, username):
        self.groups_data.add_authorized(username)

    def is_authorized(self, username):
        return username in self.groups_data.get_authorized_users()

    def get_title(self):
        return bot.getChat(self.chat_id).title

    def get_good_and_spam(self):
        return self.groups_data.get_good_and_spam()

    def set_new_db(self, new_good, new_spam):
        self.groups_data.set_new_db(new_good, new_spam)

    def is_auto_label(self):
        return self.groups_data.is_auto_label()

"""
Static functions
"""

groups_data_static_funs = FileDbGroup


def get_all_groups_codes():
    return groups_data_static_funs.get_all_groups_codes()


def get_data_all_groups():
    return groups_data_static_funs.get_data_all_groups()


def add_group(chat_id, creator_username):
    groups_data_static_funs.add_group(chat_id, creator_username)


def is_group_exists(chat_id):
    return groups_data_static_funs.is_group_exists(chat_id)