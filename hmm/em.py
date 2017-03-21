# coding=utf-8
import HMM

def BaumWelch(hmm_model, observed):
    pass

def clear_text(text):
    chars = u"·《》‘“”’【】{}～@#￥%&×（）-=——+|`~!@#$%^&*()_+-=/'\""
    chars = {_ for _ in chars}
    text = ''.join(filter(lambda x: x not in chars, text))
    for ch in u'，。！：？；,.、\n\t\r':
        text = text.replace(ch, ' ')
    return text


def read_sentence_from_file(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            for _ in clear_text(line.decode('gbk')).split():
                yield _.strip()




if __name__ == '__main__':
    sentences = read_sentence_from_file('C000023/10.txt')
    i = 0
    for sentence in sentences:
        # import pdb;pdb.set_trace()
        print i, unicode(sentence)
        i += 1
