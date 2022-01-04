import json
from pymodules import Group
from filelock import FileLock
import os

GROUPS_DATA_LOC = "database/users_and_groups/groups_data.json"
TEMP_MSGS_DB = "database/chats_msgs/temp_dbs/"
MSGS_DB = "database/chats_msgs/"
AUTO_LABEL_INDEX = 3
STATUS_INDEX = 2
ALLOWED_MSG_TYPES_LIST_INDEX = 1
AUTH_USERS_LIST_INDEX = 0
LOCK_PATH = "database/lock"


class FileDbGroup(object):
    def __init__(self, chat_id):
        self.chat_id = chat_id

    def get_data_of_chat(self):
        with open(GROUPS_DATA_LOC, 'r') as f:
            return json.loads(f.read())[self.chat_id]

    def add_authorized(self, username):
        data = self.get_data_of_chat()
        data[0].append(username)
        self.write_new_data(data)

    def get_authorized_users(self):
        return self.get_data_of_chat()[AUTH_USERS_LIST_INDEX]

    def write_new_data(self, chat_new_data):
        dict = get_data_all_groups()
        dict[self.chat_id] = chat_new_data
        with open(GROUPS_DATA_LOC, 'w') as f:
            f.write(json.dumps(dict))

    def is_rem_activated(self):
        return self.get_data_of_chat()[STATUS_INDEX] == "ACTIVATED"

    def is_auto_label(self):
        return self.get_data_of_chat()[AUTO_LABEL_INDEX] == "AUTOLABEL"

    def deactivate_auto_label(self):
        data = self.get_data_of_chat()
        data[AUTO_LABEL_INDEX] = "NOAUTOLABEL"
        self.write_new_data(data)

    def activate_auto_label(self):
        data = self.get_data_of_chat()
        data[AUTO_LABEL_INDEX] = "AUTOLABEL"
        self.write_new_data(data)

    def deactivate_spam_remove(self):
        data = self.get_data_of_chat()
        data[STATUS_INDEX] = "DEACTIVATED"
        self.write_new_data(data)

    def activate_spam_remove(self):
        data = self.get_data_of_chat()
        data[STATUS_INDEX] = "ACTIVATED"
        self.write_new_data(data)

    def get_good_ls(self):
        return open(MSGS_DB + str(self.chat_id) + "_good.txt", "r", encoding="utf8").read().split("\n")

    def get_spam_ls(self):
        return open(MSGS_DB + str(self.chat_id) + "_spam.txt", "r", encoding="utf8").read().split("\n")

    def add_to_temp_good(self, time, txt):
        with FileLock(LOCK_PATH):
            p = TEMP_MSGS_DB + self.chat_id + "_good_temp.txt"
            if is_f_empty(p):
                with open(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt", 'a', encoding="utf8") as f:
                    f.write(txt.replace("\n", " LINEBREAK ") + "," + str(time))
            else:
                with open(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt", 'a', encoding="utf8") as f:
                    f.write("\n" + txt.replace("\n", " LINEBREAK ") + "," + str(time))

    def add_to_temp_spam(self, time, txt):
        with FileLock(LOCK_PATH):
            p = TEMP_MSGS_DB + self.chat_id + "_spam_temp.txt"
            if is_f_empty(p):
                with open(p, 'a', encoding="utf8") as f:
                    f.write(txt.replace("\n", " LINEBREAK ") + "," + str(time))
            else:
                with open(p, 'a', encoding="utf8") as f:
                    f.write("\n" + txt.replace("\n", " LINEBREAK ") + "," + str(time))

    # Returns a one string for all the good and one for all the spam messages
    def get_good_and_spam(self):
        with open(MSGS_DB + self.chat_id + "_good.txt", encoding="utf8") as f:
            good = f.readlines()
        with open(MSGS_DB + self.chat_id + "_spam.txt", encoding="utf8") as f:
            spam = f.readlines()
        return "\n".join([x.strip() for x in good]), "\n".join([x.strip() for x in spam])

    def set_new_db(self, new_good=None, new_spam=None):
        if new_good is not None:
            with open(MSGS_DB + self.chat_id + "_good.txt", 'w', encoding="utf8") as f:
                f.write(new_good.replace("\r\n", "\n"))
        if new_spam is not None:
            with open(MSGS_DB + self.chat_id + "_spam.txt", 'w', encoding="utf8") as f:
                f.write(new_spam.replace("\r\n", "\n"))

    def rem_spam_from_tempgood_update_main_dbs(self, ):
        f = open(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt", "r", encoding="utf8")
        lines = f.readlines()
        f.close()
        f = open(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt", "w", encoding="utf8")
        temp = open(TEMP_MSGS_DB + self.chat_id + "_spam_temp.txt", "r", encoding="utf8")
        spaml = temp.readlines()
        temp.close()
        for line in lines:
            if str(line) not in [str(l) for l in spaml]:
                f.write(line.rsplit("\n", 1)[0])
        f.close()
        # Append to the main spam and good dbs of this group the temp dbs
        with open(MSGS_DB + self.chat_id + "_good.txt", 'a', encoding="utf8") as f:
            with open(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt", "r", encoding="utf8") as t:
                if not is_f_empty(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt"):
                    if is_f_empty(MSGS_DB + self.chat_id + "_good.txt"):
                        f.write(t.read())
                    else:
                        f.write("\n" + t.read())
        with open(MSGS_DB + self.chat_id + "_spam.txt", 'a', encoding="utf8") as f:
            with open(TEMP_MSGS_DB + self.chat_id + "_spam_temp.txt", "r", encoding="utf8") as t:
                if not is_f_empty(TEMP_MSGS_DB + self.chat_id + "_spam_temp.txt"):
                    if is_f_empty(MSGS_DB + self.chat_id + "_spam.txt"):
                        f.write(t.read())
                    else:
                        f.write("\n" + t.read())
        open(TEMP_MSGS_DB + self.chat_id + "_good_temp.txt", "w", encoding="utf8").close()
        open(TEMP_MSGS_DB + self.chat_id + "_spam_temp.txt", "w", encoding="utf8").close()


"""
Static functions
"""


def is_f_empty(p):
    with open(p, 'r', encoding="utf8") as f:
        return len(f.read()) == 0


def get_all_groups_codes():
    return list(get_data_all_groups().keys())


def create_db_files(chat_id):
    open(MSGS_DB + str(chat_id) + "_good.txt", "w", encoding="utf8").close()
    open(MSGS_DB + str(chat_id) + "_spam.txt", "w", encoding="utf8").close()
    open(TEMP_MSGS_DB + str(chat_id)+ "_good_temp.txt", "w", encoding="utf8").close()
    open(TEMP_MSGS_DB + str(chat_id) + "_spam_temp.txt", "w", encoding="utf8").close()


def get_data_all_groups():
    with open(GROUPS_DATA_LOC, 'r') as f:
        return json.loads(f.read())


def add_group(chat_id, creator_username):
    data = get_data_all_groups()
    data[chat_id] = [[creator_username], ["ALL"], "NOTACTIVATED", "AUTOLABEL"]
    with open(GROUPS_DATA_LOC, 'w') as f:
        f.write(json.dumps(data))
    create_db_files(chat_id)


def is_group_exists(chat_id):
    return chat_id in get_data_all_groups()