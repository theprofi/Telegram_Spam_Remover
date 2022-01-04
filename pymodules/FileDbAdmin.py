import json
from pymodules import CredsManager
from pymodules import Admin

ADMINS_DATA_LOC = "database/users_and_groups/admins_data.json"
GROUPS_LIST_INDEX = 1
HASH_INDEX = 0


class FileDbAdmin(object):
    def __init__(self, username):
        self.username = username

    def get_data_of_admin(self):
        with open(ADMINS_DATA_LOC, 'r') as f:
            return json.loads(f.read())[self.username]

    def add_group(self, chat_id):
        data = self.get_data_of_admin()
        data[GROUPS_LIST_INDEX].append(chat_id)
        self.write_new_data(data)

    def get_groups(self):
        return self.get_data_of_admin()[GROUPS_LIST_INDEX]

    def write_new_data(self, admin_new_data):
        dict = get_data_all_admins()
        dict[self.username] = admin_new_data
        with open(ADMINS_DATA_LOC, 'w') as f:
            f.write(json.dumps(dict))

    def update_pw(self, pw):
        data = self.get_data_of_admin()
        data[0] = CredsManager.calculate_hash(pw)
        self.write_new_data(data)

    def get_pw_hash(self):
        return self.get_data_of_admin()[HASH_INDEX]

"""
Static functions
"""


def get_data_all_admins():
    with open(ADMINS_DATA_LOC, 'r') as f:
        return json.loads(f.read())


def is_admin_exists(username):
    return username in get_data_all_admins()


def add_creator(username):
    data = get_data_all_admins()
    data[username] = [CredsManager.get_rand_letters_nums(), []]
    with open(ADMINS_DATA_LOC, 'w') as f:
        f.write(json.dumps(data))


def add_groups_to_creator(chat_id, username):
    if not is_admin_exists(username):
        add_creator(username)
    cur = Admin.Admin(username)
    cur.add_group(chat_id)
