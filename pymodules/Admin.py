from pymodules import FileDbAdmin


class Admin(object):
    def __init__(self, username):
        self.admin_username = str(username)
        self.admins_data = FileDbAdmin.FileDbAdmin(username)

    def add_group(self, chat_id):
        self.admins_data.add_group(chat_id)

    def get_groups(self):
        return self.admins_data.get_groups()

    def update_pw(self, pw):
        self.admins_data.update_pw(pw)

    def get_pw_hash(self):
        return self.admins_data.get_pw_hash()


"""
Static functions
"""

admins_data_static_funs = FileDbAdmin


def get_data_all_admins():
    return admins_data_static_funs.get_data_all_admins()


def is_admin_exists(username):
    return admins_data_static_funs.is_admin_exists(username)


def add_creator(username):
    admins_data_static_funs.add_creator(username)


def add_group_to_creator(chat_id, username):
    admins_data_static_funs.add_groups_to_creator(chat_id, username)




