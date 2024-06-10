import numpy as np
from nltk.tokenize import word_tokenize

from prism import reassemble


def load_glove(dim=300, token=6):
    emb = []
    words = []
    with open("glove/glove.{}B.{}d.txt".format(token, dim), "r") as f:
        for r in f:
            split = r.split()
            emb.append(np.array(list(map(float, split[-dim:]))))
            words.append("".join(split[:-dim]))
    emb = np.array(emb)
    return emb, words


class PUP:
    def __init__(self, dim=50):
        self.dim = dim
        self.emb, self.word = load_glove(dim=dim)
        self.word_to_index = {w: i for i, w in enumerate(self.word)}

    def closest_word(self, vec):
        distances = np.linalg.norm(self.emb - vec, axis=1)
        # Find the index of the minimum distance
        min_index = np.argmin(distances)
        return self.word[min_index]

    def encode(self, text, eps=0.1):
        tokens = word_tokenize(text)
        res = []
        for token in tokens:
            if token.lower() not in self.word_to_index:
                res.append(token)
            else:
                noise_norm = np.random.gamma(shape=self.dim, scale=1 / eps)
                noise = np.random.randn(self.dim)
                noise = noise / np.linalg.norm(noise) * noise_norm
                vec = self.emb[self.word_to_index[token.lower()]] + noise
                res.append(self.closest_word(vec))
        text = reassemble(text, tokens, res)
        return text

    def decode(self, text):
        return text
