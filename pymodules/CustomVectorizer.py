import numpy as np
from nltk.tokenize import word_tokenize


class CustomVectorizer:
    def __init__(self):
        self.vocabulary_size = 0
        self.word2location = {}

    def prepare_vocabulary(self, data):
        idx = 0
        for sentence in data:
            for word in word_tokenize(sentence):
                if word not in self.word2location:
                    self.word2location[word] = idx
                    idx += 1
        self.vocabulary_size = idx

    def convert2vec(self, msg):
        res_vec = [0] * self.vocabulary_size
        # res_vec = np.zeros(len(self.vocabulary_size))
        for word in word_tokenize(msg):
            if word in self.word2location:
                res_vec[self.word2location[word]] += 1
        return res_vec

    def convert_list(self, ls):
        ret = []
        for l in ls:
            ret.append(self.convert2vec(l))
        return ret
