import hashlib
from pymodules import Admin
import random
import string
from passlib.hash import argon2


def calculate_hash(pw):
    return argon2.hash(pw.encode("utf-8"))


def verify_entered_creds(username, entered_pw):
    if not Admin.is_admin_exists(username):
        return False
    return argon2.verify(entered_pw.encode("utf-8"), Admin.Admin(username).get_pw_hash())


def get_rand_letters_nums(length=8):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase.replace("I", "")
                                                + string.digits) for _ in range(length))
