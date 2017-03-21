# coding=utf-8

import math
import numpy as np

MIN_FLOAT = -3.14e100

class ExtendDict(object):
    def __init__(self, dict_):
        self.dict = dict_

    def __getitem__(self, item):
        if item in self.dict:
            return self.dict[item]
        else:
            return MIN_FLOAT

    @staticmethod
    def MakeExtendDict(dict_):
        def make(dict_):
            for k, v in dict_.iteritems():
                if isinstance(v, dict):
                    dict_[k] = make(v)
            return ExtendDict(dict_)
        return make(dict_)

class HMM(object):
    def __init__(self, trans, emit, init, states):
        self.trans = trans
        self.emit = emit
        self.init = init
        self.states = states

    def calc_alpha(self, observed):
        T = len(observed)
        alpha = [{}] * T

        for state in self.states:
            alpha[0][state] = self.init[state] + self.emit[state][observed[0]]

        for t in xrange(1, T):
            temp = {}
            for i in self.states:
                temp[i] = math.log(sum((math.exp(alpha[t-1][j] + self.trans[j][i]) for j in self.states))) + self.emit[i][observed[t]]
            alpha[t] = temp

        return alpha

    def calc_beta(self, observed):
        T = len(observed)
        beta = [{}] * T

        for state in self.states:
            beta[T - 1] = 0

        for t in xrange(T-2, -1, -1):
            temp = {}
            for i in self.states:
                temp[i] = math.log(sum((math.exp(self.trans[i][j] + self.emit[j][observed[t+1][j]] + beta[t+1][j]) for j in self.states)))
            beta[t] = temp

        return beta

    def calc_observe_prob_by_alpha(self, alpha):
        prob = math.log(sum((math.exp(alpha[-1][j]) for j in self.states)))
        return prob

    def calc_gamma(self, observed):
        alpha = self.calc_alpha(observed)
        beta = self.calc_beta(observed)
        observed_prob = self.calc_observe_prob_by_alpha(alpha)

        T = len(observed)
        gamma = [{}] * T

        for t in xrange(T):
            temp = {}
            for i in self.states:
                temp[i] = alpha[t][i] + beta[t][i] - observed_prob
            gamma[t] = temp

        return gamma

    def calc_xi(self, observed):
        alpha = self.calc_alpha(observed)
        beta = self.calc_beta(observed)
        observed_prob = self.calc_observe_prob_by_alpha(alpha)

        T = len(observed)
        xi = [{}] * T

        for t in xrange(T-1):
            temp = {}
            for i in self.states:
                for j in self.states:
                    temp.setdefault(i, {})
                    temp[i][j] = alpha[t][i] + self.trans[i][j] + self.emit[j][observed[t+1]] + beta[t+1][j] - observed_prob
            xi[t] = temp

        return xi

    def viterbi(self, observed):
        T = len(observed)
        a = [{}] * T
        parents = [{}] * T

        for state in self.states:
            a[0][state] = self.init[state] + self.emit[state][observed[0]]
            parents[0][state] = 0

        for t in xrange(1, T):
            new_a = {}
            parent = {}
            for i in states:
                max_value, max_state = max(((a[t-1][j] + self.trans[j][i], j) for j in self.states), key=lambda x: x[0])
                new_a[i] = max_value + emit[i][observed[t]]
                parent[i] = max_state
            a[t] = new_a
            parents[t] = parent

        max_p, max_state = max(((a[T-1][i], i) for i in self.states), key=lambda x: x[0])

        path = [max_state]
        cur_state = max_state
        for t in xrange(T-1, 0, -1):
            parent = parents[t][cur_state]
            path.append(parent)
            cur_state = parent
        path.reverse()
        return path

class CutError(Exception):
    pass

def _cut(sentence, labels):
    def n2word(n):
        return sentence[n]
    pairs = labels
    i = 0
    N = len(sentence)
    while i < N:
        b_word = i
        i += 1
        if pairs[b_word] == 'S':
            yield sentence[b_word]
        elif pairs[b_word] == 'B':
            word = sentence[b_word]
            while i < N and pairs[i] == 'M':
                word += sentence[i]
                i += 1
            if i >= N:
                yield word
            elif pairs[i] == 'E':
                word += sentence[i]
                yield word
                i += 1
            else:
                print i
                print b_word
                # import ipdb;ipdb.set_trace()
                raise CutError('no end word')
        else:
            print i
            raise CutError('start word is not B')

def cut(sentence, labels):
    return ' '.join(_cut(sentence, labels))

def load_data():
    from prob_trans import P as trans
    from prob_emit import P as emit
    from prob_start import P as init
    return trans, emit, init

def logify(arr):
    if isinstance(arr, list):
        new_arr = []
        for x in arr:
            new_arr.append(logify(x))
    elif isinstance(arr, dict):
        new_arr = {}
        for k, v in arr.iteritems:
            new_arr[k] = logify(v)
    else:
        try:
            new_arr = math.log(arr)
        except ValueError:
            new_arr = 0
    return new_arr

if __name__ == '__main__':
    try:
        trans, emit, init = load_data()
    except ImportError:
        pass
    trans = ExtendDict.MakeExtendDict(trans)
    emit = ExtendDict.MakeExtendDict(emit)
    init = ExtendDict.MakeExtendDict(init)
    states = 'BMES'
    hmm_model = HMM(trans, emit, init, states)
    while True:
        try:
            seq = raw_input()
        except IOError:
            break
        seq = seq.decode('utf-8')
        path = hmm_model.viterbi(seq)
        print path
        print cut(seq, path)
    # trans = [
    #     [0.5, 0.2, 0.3],
    #     [0.3, 0.5, 0.2],
    #     [0.2, 0.3, 0.5]
    # ]
    # emit = [
    #     [0.5, 0.5],
    #     [0.4, 0.6],
    #     [0.7, 0.3]
    # ]
    # init = [
    #     0.2, 0.4, 0.4
    # ]
    # states = [0, 1, 2]
    # hmm = HMM(logify(trans), logify(emit), logify(init), states)
    # res = hmm.calc_alpha([0, 1, 0])
    # new_res = []
    # for pair in res:
    #     temp = {}
    #     for k, v in pair.iteritems():
    #         temp[k] = math.exp(v)
    #     new_res.append(temp)
    # print new_res
