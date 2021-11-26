from sentiment.Morph.khaiii_morph import khaiii_morph
import kss

def splitSentence(document):
    splittedSentence = []
    for sent in kss.split_sentences(document):
        # print('문장 구분 :', sent)
        splittedSentence.append(sent)
    return splittedSentence

def getCorpus_Khaiii(corpus):
    result = []
    try:
        if (len(corpus) < 100000):
            corpus = corpus.replace("　", "").replace(" ", "").replace("​", "")
            splitCorpus = splitSentence(corpus)
            for originCorpus in splitCorpus:
                processed_corpus0 = khaiii_morph(originCorpus)  # morph
                result.append(processed_corpus0)
            return result
        else:
            print(len(corpus))
            return False
    except:
        return False