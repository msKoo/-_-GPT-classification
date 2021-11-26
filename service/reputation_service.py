import os
import re
from silence_tensorflow import silence_tensorflow
from collections import OrderedDict
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from service.finetuning_model.train_module import TFGPT2Classifier, tokenizer, vocab

silence_tensorflow()
SENT_MAX_LEN = 39

def clean_text(sent):
    sent_clean = re.sub("[^가-힣ㄱ-ㅎㅏ-ㅣ\\s]", "", sent)
    return sent_clean

def translateTextToToken(text):
    test_data_sents = []
    test_tokenized_text = vocab[tokenizer(clean_text(text))]

    tokens = [vocab[vocab.bos_token]]
    tokens += pad_sequences([test_tokenized_text],
                            SENT_MAX_LEN,
                            value=vocab[vocab.padding_token],
                            padding='post').tolist()[0]
    tokens += [vocab[vocab.eos_token]]

    test_data_sents.append(tokens)
    return test_data_sents

def translateListToToken(List):
    data_sents = []
    for train_sent in List:
        train_tokenized_text = vocab[tokenizer(clean_text(train_sent))]

        tokens = [vocab[vocab.bos_token]]
        tokens += pad_sequences([train_tokenized_text],
                                SENT_MAX_LEN,
                                value=vocab[vocab.padding_token],
                                padding='post').tolist()[0]
        tokens += [vocab[vocab.eos_token]]

        data_sents.append(tokens)

    return data_sents

def reputation_generator(text):
    print(text)
    result = {}
    finetuning_model_path = './service/finetuning_model/classification_model/'
    classification_model_name = 'PosNeg'

    classification_model_path = os.path.join(finetuning_model_path, classification_model_name)

    classification_model = TFGPT2Classifier(dir_path=classification_model_path, num_class=2)

    probability_model = tf.keras.Sequential([classification_model, tf.keras.layers.Softmax()]) #predict 함수

    if isinstance(text, str):
        token = translateTextToToken(text)
    else:
        ##### 테스트용 else 문
        token = translateListToToken(text)

        predictions = probability_model.predict(token)

        return tf.argmax(predictions, 1)

    print(classification_model.predict(token, batch_size=1024))

    predictions = probability_model.predict(token)

    result['pos'] = predictions[0][0]
    result['neg'] = predictions[0][1]

    # float 형 변환을 위한 convert
    # data_convert = {k: round(float(v),3) for k, v in result.items()}

    print(result)

    return result


def posneg_sentiment(text):
    result = {}

    BASE_MODEL_PATH = './service/finetuning_model/detailed_classification_model/gpt_ckpt'
    weightPath = './service/data/out/posneg/'
    new_model = TFGPT2Classifier(dir_path=BASE_MODEL_PATH, num_class=6)


    new_model.load_weights(weightPath)

    probability_model = tf.keras.Sequential([new_model, tf.keras.layers.Softmax()]) #predict 함수

    if isinstance(text, str):   # 한 문장인 경우
        token_list = translateTextToToken(text)
    else:                       # 문장 리스트인 경우
        token_list = translateListToToken(text)

    predictions = probability_model.predict(token_list, batch_size=1024)

    result['pos'] = predictions[0][0]
    result['neg'] = predictions[0][1]

    # label : 기쁨 : 0, 불안 : 1, 당황 : 2, 슬픔 : 3, 분노 : 4, 상처 : 5
    # value = tf.argmax(result,1)

    return result


def detailed_sentiment(text):
    BASE_MODEL_PATH = './service/finetuning_model/detailed_classification_model/gpt_ckpt'
    weightPath = './service/data/out/save/'
    new_model = TFGPT2Classifier(dir_path=BASE_MODEL_PATH, num_class=6)

    new_model.load_weights(weightPath)

    if isinstance(text, str):   # 한 문장인 경우
        token_list = translateTextToToken(text)
    else:                       # 문장 리스트인 경우
        token_list = translateListToToken(text)

    result = new_model.predict(token_list, batch_size=1024)

    # label : 기쁨 : 0, 불안 : 1, 당황 : 2, 슬픔 : 3, 분노 : 4, 상처 : 5
    value = tf.argmax(result,1)

    return result, tf.keras.backend.eval(value)

def repu_main(text):
    # result = reputation_generator(text)
    result = posneg_sentiment(text)
    detail, value = detailed_sentiment(text)
    data_convert = {k: round(float(v), 3) for k, v in result.items()}

    newRepu = {}

    newRepu['기쁨'] = round(float(detail[0][0]), 3)
    newRepu['불안'] = round(float(detail[0][1]), 3)
    newRepu['당황'] = round(float(detail[0][2]), 3)
    newRepu['슬픔'] = round(float(detail[0][3]), 3)
    newRepu['분노'] = round(float(detail[0][4]), 3)
    newRepu['상처'] = round(float(detail[0][5]), 3)

    detailRepu = OrderedDict(sorted(newRepu.items(), key=lambda t:t[1], reverse=True))

    data_convert['repu'] = detailRepu

    print(data_convert)

    return data_convert