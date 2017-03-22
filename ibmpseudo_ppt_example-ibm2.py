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


def read_bitext_file(train_target, train_source, null_alignment=True):
    lines_source = open(train_source, "r").readlines()
    lines_target = open(train_target, "r").readlines()
    if null_alignment:
        bitext = [(['NULL'] + lines_target[i].strip().split(), lines_source[i].strip().split()) for
                  i in range(len(lines_source))]  # allows null assignment
    else:
        bitext = [(lines_target[i].strip().split(), lines_source[i].strip().split()) for
                  i in range(len(lines_source))]
    return bitext


class IBM():
    def __init__(self, bitext, max_iter=20):
        self.bitext = bitext
        self.max_iter = max_iter
        self.src_counter = Counter(chain(*[pair[1] for pair in bitext]))
        self.src_vocab = self.src_counter.keys()
        print "F vocab size " + str(len(self.src_vocab))
        self.tgt_counter = Counter(chain(*[pair[0] for pair in bitext]))
        self.tgt_vocab = self.tgt_counter.keys()

        print "E vocab size " + str(len(self.tgt_vocab))

        print "bitext pair " + str(len(bitext))
        self.epsilon = 1.0 / max(
            [len(line) for line in
             [pair[1] for pair in bitext]])  # max # of words within src sentences in the training corpus
        self.theta = defaultdict(lambda: defaultdict(lambda: 1.0 / (len(self.tgt_vocab))))
        value=1.0 / max(
            [len(line) for line in
             [pair[0] for pair in bitext]])
        self.beta = defaultdict(lambda: value)
        print 1.0 / (len(self.tgt_vocab))

    def train(self):

        for iter in range(self.max_iter):

            self.c_e_f = defaultdict(lambda: defaultdict(lambda: 0.0))  # E step: initialize all counts c_ef to zero
            self.c_f = defaultdict(
                lambda: 0.0)  # Should we keep either c_e updated from 0 or only get the vocab counter
            self.c_length_e_f = defaultdict(lambda: 0.0)  # E step: initialize all counts c_ef to zero
            self.c_length_e = defaultdict(
                lambda: 0.0)

            for idx, (e, f) in enumerate(self.bitext):
                # print iter,idx, idx * 1.0 / len(self.bitext)

                denominator = defaultdict(lambda: 0.0)
                denominator_2 = defaultdict(lambda: 0.0)
                for idx_i, i in enumerate(e):
                    denominator[i] = 0
                    denominator_2[i] = 0
                    for idx_j, j in enumerate(f):
                        denominator[i] += self.theta[i][j]
                        denominator_2[i] += self.beta[(idx_i, idx_j, len(f), len(e))]
                for idx_i, i in enumerate(e):
                    for idx_j, j in enumerate(f):
                        self.c_e_f[i][j] += self.theta[i][j] / denominator[i] * self.beta[
                            (idx_i, idx_j, len(f), len(e))] / denominator_2[i]
                        self.c_f[j] += self.theta[i][j] / denominator[i] * self.beta[
                            (idx_i, idx_j, len(f), len(e))] / denominator_2[i]
                        self.c_length_e_f[(idx_i, idx_j, len(f), len(e))]+=self.theta[i][j] / denominator[i] * self.beta[
                            (idx_i, idx_j, len(f), len(e))] / denominator_2[i]
                        self.c_length_e[(idx_i,len(f),len(e))]+=self.theta[i][j] / denominator[i] * self.beta[
                            (idx_i, idx_j, len(f), len(e))] / denominator_2[i]
            for i in self.theta.keys():
                for j in self.theta[i].keys():
                    self.theta[i][j] = self.c_e_f[i][j] / self.c_f[j]
            for key in self.c_length_e_f.keys():
                self.beta[key]=self.c_length_e_f[key]/self.c_length_e[(key[0],key[2],key[3])]

            # ll = self.sumLL()
            print "iter " + str(iter)
            # print self.theta

    def sumLL(self):
        sumLL = 0
        total = 0

        for idx, (e, f) in enumerate(self.bitext):

            sumLL += np.log(self.epsilon) - len(f) * 1.0 / np.log(len(e))

            for i in e:
                total += 1
                sum_theta = 0
                for j in f:
                    sum_theta += self.theta[i][j]
                sumLL += np.log(sum_theta)

        print sumLL, total, sumLL / total

        return sumLL / len(self.tgt_vocab)

    def align(self, align_output, align_output_groundtruth, isPrint):

        f_write = open(align_output, "w")
        for idx, (e, f) in enumerate(self.bitext):
            # print e,f
            for idx2, j in enumerate(f):

                # ARGMAX_j θ[i,j] or other alignment in Section 11.6 (e.g., Intersection, Union, etc)
                max_i, max_prob = self.argmax_i(e, j)  # argmax_e(P(e|f))
                f_write.write(str(max_i) + "-" + str(idx2))
                if not idx2 == len(f) - 1:
                    f_write.write(" ")
            f_write.write("\n")

            # return alignments
        f_write.close()
        f_write_lines = open(align_output, "r").readlines()

        if isPrint:

            f_ground_truth_lines = open(align_output_groundtruth, "r").readlines()
            total = 0
            for i in range(len(f_ground_truth_lines)):
                if f_ground_truth_lines[i].strip().split() == f_write_lines[i].strip().split():
                    total += 1
            print 1.0 * total / len(f_ground_truth_lines)

    def argmax_i(self, e, j):
        denominator = 0

        max_prob = -1

        for idx, i in enumerate(e):
            # print i,self.theta[i][j]
            denominator += self.theta[i][j]
            if self.theta[i][j] > max_prob:
                max_prob = self.theta[i][j]
                max_i = idx

        return max_i, max_prob


def test_mini():
    bitext = []
    # bitext.append((['klein', 'ist', 'das', 'haus'], ['the', 'house', 'is', 'small']))
    # bitext.append((['das', 'haus', 'ist', 'ja', 'groß'], ['the', 'house', 'is', 'big']))
    # bitext.append((['das', 'buch', 'ist', 'ja', 'klein'], ['the', 'book', 'is', 'small']))
    bitext.append((['the', 'house'], ['das', 'haus']))
    bitext.append((['the', 'book'], ['das', 'buch']))
    bitext.append((['a', 'book'], ['ein', 'buch']))
    return bitext  # ibm1 = IBMModel1(bitext, 5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # parser.add_argument('--train_source', type=str, default="./en-de/train.en-de.low.filt.de")
    parser.add_argument('--train_source', type=str, default="./en-de/valid.en-de.low.de")

    # parser.add_argument('--train_target', type=str, default="./en-de/train.en-de.low.filt.en")
    parser.add_argument('--train_target', type=str, default="./en-de/valid.en-de.low.en")
    parser.add_argument('--align_output', type=str, default="./output/alignment.txt")
    parser.add_argument('--align_output_groundtruth', type=str, default="./output-valid/alignment.txt")
    parser.add_argument('--null_alignment', action='store_true')

    parser.add_argument('--max_iter', type=int, default=30)

    args = parser.parse_args()

    print "allow null alignment " + str(args.null_alignment)

    bitext = read_bitext_file(args.train_target,
                              args.train_source,
                              args.null_alignment)  # pairs of sentences  # bitext = [ ( ['with', 'vibrant', ..], ['mit', 'hilfe',..] ), ([], []) , ..]

    # print bitext[:2]
    # bitext = test_mini()


    ibm = IBM(bitext, max_iter=args.max_iter)
    ibm.train()
    # print ibm.theta
    ibm.align(args.align_output, args.align_output_groundtruth, False)
