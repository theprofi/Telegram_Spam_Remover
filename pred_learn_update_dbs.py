from pymodules import Group
from sklearn import linear_model
from pymodules import CustomVectorizer
from sklearn.externals import joblib
from pathlib import Path
from sklearn.neural_network import MLPClassifier
from filelock import FileLock
import schedule
import time

SAVED_MODULES = "database/saved_modules"
LOCK_PATH = "database/lock"


def update_main_dbs():
    all_grps_code = Group.get_all_groups_codes()
    for code in all_grps_code:
        cur = Group.Group(code)
        with FileLock(LOCK_PATH):
            cur.rem_spam_from_tempgood_update_main_dbs()
            save_model(cur.get_good_ls(), cur.get_spam_ls(), code)
        return


def save_model(good, spam, group_code):
    msgs_txt = [msg.rsplit(',', 1)[0] for msg in good] + [msg.rsplit(',', 1)[0] for msg in spam]
    msgs_time = []
    for i, m in enumerate(good + spam):
        if len(m) > 3:
            msgs_time.append(m.rsplit(',', 1)[1])
    vectorizer = CustomVectorizer.CustomVectorizer()
    vectorizer.prepare_vocabulary(msgs_txt)
    X = vectorizer.convert_list(msgs_txt)
    for i in range(len(X)):
        X[i] += [int(msgs_time[i])]
    clf = MLPClassifier(hidden_layer_sizes=(3500, 3500, 1500, 1000, 500))
    clf.fit(X, [0] * len(good) + [1] * len(spam))
    joblib.dump(clf, SAVED_MODULES + "/clf" + group_code)
    joblib.dump(vectorizer, SAVED_MODULES + "/vectorizer" + group_code)


def is_spam(msg, time, group_code):
    clf_file = Path(SAVED_MODULES + "/clf" + group_code)
    vectorizer_file = Path(SAVED_MODULES + "/vectorizer" + group_code)
    if clf_file.is_file() and vectorizer_file.is_file():
        clf = joblib.load(SAVED_MODULES + "/clf" + group_code)
        vectorizer = joblib.load(SAVED_MODULES + "/vectorizer" + group_code)
        return \
            clf.predict([vectorizer.convert2vec(msg.replace("\n", " LINEBREAK ")) + [int(time)]])[0] == 1
    else:
        print("No saved modules for group", group_code)
        return False


def main():
    schedule.every().day.at("02:00").do(update_main_dbs)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
