from collections import OrderedDict
from khaiii import KhaiiiApi

api = KhaiiiApi()

# 형태소 분석 과정 (형태소 분해부)
def khaiii_morph(text):
    file_data = OrderedDict()
    data=api.analyze(text)
    mor_list = [[] for _ in range(len(data))] #test version

    for i, word in enumerate(data):
        morph_dic = {"index" : i}
        morph_str = ""
        for morph in word.morphs:
            morph_str += f"{morph.lex}/{morph.tag}, "
            mor_list[i].append((morph.lex, morph.tag)) #test version
            
        morph_dic["morph"] = morph_str[:-2]
        file_data[i] = morph_dic

    return mor_list