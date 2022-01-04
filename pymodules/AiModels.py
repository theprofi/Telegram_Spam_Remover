from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn import linear_model
from datetime import datetime

BOTH = 0
GAUSSIAN = 1
LOGREG = 2


def learn_on_the_fly(good, spam, msg, model=GAUSSIAN, discrete=True, threshold=0.75):
    sentences = [msg.rsplit(',', 1)[0] for msg in good]
    len_0 = len(sentences)
    sentences += [msg.rsplit(',', 1)[0] for msg in spam]
    len_1 = len(sentences) - len_0
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(sentences).toarray().tolist()
    for i, vec in enumerate(X):
        if i < len(good):
            vec.append(datetime.utcfromtimestamp(good[i].rsplit(',', 1)[1]).strftime('%H'))
        else:
            vec.append(datetime.utcfromtimestamp(spam[i - len(good)].rsplit(',', 1)[1]).strftime('%H'))
    Y = [0] * len_0 + [1] * len_1
    clf = linear_model.LogisticRegression() if model == LOGREG else GaussianNB()
    clf.fit(X, Y)
    if discrete:
        return clf.predict(vectorizer.transform([msg.encode("utf-8")]).toarray())[0] == 1
    else:
        return not clf.predict_proba(vectorizer.transform([msg.encode("utf-8")]).toarray())[0][0] >= threshold
