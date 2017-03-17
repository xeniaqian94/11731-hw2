# -*- encoding: utf-8 -*-
'''
  Alignment: P( E | F) = Σ_θ P( θ, F | E) (Equation 98)
  IBM model 1: P( θ, F | E)
  (1) Initialize θ[i,j] = 1 / (|E| + 1) (i for E and j for F) (Equation 100) 
  (2) Expectation-Maximization (EM)
    [E] C[i,j] =  θ[i,j] / Σ_i θ[i,j] (Equation 110)
    [M] θ[i,j] =  C[i,j] / Σ_j C[i,j] (Equation 107)
  (3) Calculate data likelihood (Equation 106)
'''
import argparse

from collections import Counter, defaultdict
from collections import defaultdict
from itertools import count, izip, chain
from nltk.translate import AlignedSent
import numpy as np


def read_bitext_file(train_source, train_target):
    lines_source = open(train_source, "r").readlines()

    lines_target = open(train_target, "r").readlines()
    bitext = [(lines_source[i].strip().split(), lines_target[i].strip().split() + ["NULL"]) for
              i in range(len(lines_source))]

    return bitext


class IBM():
    def __init__(self, bitext, max_iter=20):
        self.bitext = bitext
        self.max_iter = max_iter
        self.src_counter = Counter(chain(*[pair[0] for pair in bitext]))
        self.src_vocab = self.src_counter.keys()
        self.tgt_counter = Counter(chain(*[pair[1] for pair in bitext]))
        self.tgt_vocab = self.tgt_counter.keys()
        self.epsilon = 1.0 / max(
            [len(line) for line in [pair[0] for pair in bitext]])  # max # of words within the training corpus
        # self.theta = defaultdict(lambda: defaultdict(lambda: 1.0 / (len(self.tgt_vocab))))

    def train(self):

        # for i in self.tgt_vocab:
        #     for j in self.src_vocab:
        #         self.theta[i][j] = 1.0 / (len(self.tgt_vocab))  # including NULl token as well
        self.c_f_e_old = defaultdict(lambda: defaultdict(lambda: 0.0))  # E step: initialize all counts c_ef to zero
        self.c_e_old = defaultdict(lambda: 0.0)

        for iter in range(self.max_iter):

            self.c_f_e = defaultdict(lambda: defaultdict(lambda: 0.0))  # E step: initialize all counts c_ef to zero
            self.c_e = defaultdict(lambda: 0.0)  # Should we keep c_e updated from 0 or only get the vocab counter

            for idx, (f, e) in enumerate(self.bitext):
                if idx % (len(self.bitext) / 10) == 0:
                    print idx, idx * 1.0 / len(self.bitext)

                for j in f:
                    denominator = 0
                    for i in e:

                        if iter == 0:
                            theta = 1.0 / (len(self.tgt_vocab))
                        else:
                            theta = self.c_f_e_old[i][j] / self.c_e_old[i]
                        # denominator += self.theta[i][j]
                        denominator += theta
                    for i in e:
                        # self.c_f_e[i][j] += self.theta[i][j] / denominator  # (Equation 110)  align from src j to tgt i
                        if iter == 0:
                            theta = 1.0 / (len(self.tgt_vocab))
                        else:
                            theta = self.c_f_e_old[i][j] / self.c_e_old[i]
                        self.c_f_e[i][j] += theta / denominator
                        self.c_e[i] += theta / denominator

                        # for i in self.tgt_vocab:
                        #     # print self.c_e[i], self.tgt_counter[i]
                        #     for j in self.src_vocab:
                        #         self.theta[i][j] = self.c_f_e[i][j] / self.c_e[i]

            self.c_f_e_old = self.c_f_e
            self.c_e_old = self.c_e
            ll = self.sumLL()
            print "iter " + str(iter) + ": " + str(ll)

    def sumLL(self):
        sumLL = 0

        for idx, (f, e) in enumerate(self.bitext):

            if idx % (len(self.bitext) / 10) == 0:
                print idx, idx * 1.0 / len(self.bitext),sumLL
            sumLL += np.log(self.epsilon) - len(f) * 1.0 / np.log(len(e))

            for j in f:
                sum_theta = 0
                for i in e:
                # sum_theta += self.theta[i][j]
                    theta = self.c_f_e_old[i][j] / self.c_e_old[i]
                    sum_theta += theta
            # print i, j,sum_theta
                sumLL += np.log(sum_theta)

        return sumLL

        #             count[e[i], f[j]] = TODO   (Equation 111)
        #             # (2) [M] θ[i,j] =  C[i,j] / Σ_j C[i,j] (Equation 107)
        #             self.theta[e[i], f[j]] = TODO
        #             # (3) Calculate log data likelihood to make sure it's increasing after each iteration (Equation 106)
        #             ll = TODO
        #             # (Optional) save/load model parameters for efficiency
        #         #
        #         #
        #         #
        #         #             # [0] Log Likelihood : -5.232084
        #         #             # [1] Log Likelihood : -4.542094
        #         #             # [2] Log Likelihood : -4.321830
        #         #             # [3] Log Likelihood : -4.244019
        #         #             # [4] Log Likelihood : -4.209469
        #         #             # [5] Log Likelihood : -4.191590
        #         #             # [6] Log Likelihood : -4.181324
        #

        # def align(self):
        #     for idx, (e, f) in enumerate(self.bitext):
        #         for i in range(len(e)):
        #             # ARGMAX_j θ[i,j] or other alignment in Section 11.6 (e.g., Intersection, Union, etc)
        #             max_j, max_prob = argmax_j(f, e[i])
        #         self.plot_alignment((max_j, max_prob), e, f)
        #     return alignments


def test_mini_nltk():
    bitext = []
    bitext.append(AlignedSent(['klein', 'ist', 'das', 'haus'], ['the', 'house', 'is', 'small']))
    print bitext[0]
    bitext.append(AlignedSent(['das', 'haus', 'ist', 'ja', 'groß'], ['the', 'house', 'is', 'big']))
    bitext.append(AlignedSent(['das', 'buch', 'ist', 'ja', 'klein'], ['the', 'book', 'is', 'small']))
    bitext.append(AlignedSent(['das', 'haus'], ['the', 'house']))
    bitext.append(AlignedSent(['das', 'buch'], ['the', 'book']))
    bitext.append(AlignedSent(['ein', 'buch'], ['a', 'book']))
    return bitext


def test_mini():
    bitext = []
    bitext.append((['klein', 'ist', 'das', 'haus'], ['the', 'house', 'is', 'small']))
    bitext.append((['das', 'haus', 'ist', 'ja', 'groß'], ['the', 'house', 'is', 'big']))
    bitext.append((['das', 'buch', 'ist', 'ja', 'klein'], ['the', 'book', 'is', 'small']))
    bitext.append((['das', 'haus'], ['the', 'house']))
    bitext.append((['das', 'buch'], ['the', 'book']))
    bitext.append((['ein', 'buch'], ['a', 'book']))
    return bitext  # ibm1 = IBMModel1(bitext, 5)
    #
    # >> > print('{0:.3f}'.format(ibm1.translation_table['buch']['book']))
    # 0.889
    # >> > print('{0:.3f}'.format(ibm1.translation_table['das']['book']))
    # 0.062
    # >> > print('{0:.3f}'.format(ibm1.translation_table['buch'][None]))
    # 0.113
    # >> > print('{0:.3f}'.format(ibm1.translation_table['ja'][None]))
    # 0.073


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--train_source', type=str, default="./en-de/train.en-de.low.filt.de")
    parser.add_argument('--train_target', type=str, default="./en-de/train.en-de.low.filt.en")
    parser.add_argument('--max_iter', type=int, default=100)

    args = parser.parse_args()

    bitext = read_bitext_file(args.train_source,
                              args.train_target)  # pairs of sentences  # bitext = [ ( ['with', 'vibrant', ..], ['mit', 'hilfe',..] ), ([], []) , ..]

    print bitext[:2]
    # bitext=test_mini()

    ibm = IBM(bitext, max_iter=args.max_iter)
    ibm.train()
    # ibm.align()
