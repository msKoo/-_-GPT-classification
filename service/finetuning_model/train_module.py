import os
import re

import numpy as np
import tensorflow as tf
import pandas as pd
import gluonnlp as nlp
from silence_tensorflow import silence_tensorflow
from gluonnlp.data import SentencepieceTokenizer
from transformers import TFGPT2LMHeadModel, TFGPT2Model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

silence_tensorflow()
loss_object = tf.keras.losses.SparseCategoricalCrossentropy(
    from_logits=True, reduction='none')

train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='accuracy')

# TOKENIZER_PATH = 'finetuning_model/gpt2_kor_tokenizer.spiece'
TOKENIZER_PATH = './service/finetuning_model/gpt2_kor_tokenizer.spiece'
tokenizer = SentencepieceTokenizer(TOKENIZER_PATH, num_best=0, alpha=0)
vocab = nlp.vocab.BERTVocab.from_sentencepiece(TOKENIZER_PATH,
                                               mask_token=None,
                                               sep_token=None,
                                               cls_token=None,
                                               unknown_token='<unk>',
                                               padding_token='<pad>',
                                               bos_token='<s>',
                                               eos_token='</s>')

class TFGPT2Classifier(tf.keras.Model):
    def __init__(self, dir_path, num_class):
        super(TFGPT2Classifier, self).__init__()

        self.gpt2 = TFGPT2Model.from_pretrained(dir_path)
        self.num_class = num_class

        self.dropout = tf.keras.layers.Dropout(self.gpt2.config.summary_first_dropout)
        self.classifier = tf.keras.layers.Dense(self.num_class,
                                                kernel_initializer=tf.keras.initializers.TruncatedNormal(
                                                    stddev=self.gpt2.config.initializer_range),
                                                name="classifier")

    def call(self, inputs):
        outputs = self.gpt2(inputs)
        pooled_output = outputs[0][:, -1]

        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)

        return logits


#GPT2 Model
class GPT2Model(tf.keras.Model):
    def __init__(self, dir_path):
        super(GPT2Model, self).__init__()
        self.gpt2 = TFGPT2LMHeadModel.from_pretrained(dir_path)

    def call(self, inputs):
        return self.gpt2(inputs)[0]

def tf_top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-99999):
    _logits = logits.numpy()
    top_k = min(top_k, logits.shape[-1])
    if top_k > 0:
        indices_to_remove = logits < tf.math.top_k(logits, top_k)[0][..., -1, None]
        _logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits = tf.sort(logits, direction='DESCENDING')
        sorted_indices = tf.argsort(logits, direction='DESCENDING')
        cumulative_probs = tf.math.cumsum(tf.nn.softmax(sorted_logits, axis=-1), axis=-1)

        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove = tf.concat([[False], sorted_indices_to_remove[..., :-1]], axis=0)
        indices_to_remove = sorted_indices[sorted_indices_to_remove].numpy().tolist()

        _logits[indices_to_remove] = filter_value
    return tf.constant([_logits])

def sentense_processing(sents,MAX_LEN):
    input_data = []
    output_data = []

    for s in sents:
        try:
            tokens = [vocab[vocab.bos_token], ] + vocab[tokenizer(s)] + [vocab[vocab.eos_token], ]
            input_data.append(tokens[:-1])
            output_data.append(tokens[1:])
        except:
            print('error : sentense', s)

    input_data = pad_sequences(input_data, MAX_LEN, value=vocab[vocab.padding_token])
    output_data = pad_sequences(output_data, MAX_LEN, value=vocab[vocab.padding_token])

    input_data = np.array(input_data, dtype=np.int64)
    output_data = np.array(output_data, dtype=np.int64)

    return input_data, output_data

def loss_function(real, pred):
    mask = tf.math.logical_not(tf.math.equal(real, vocab[vocab.padding_token]))
    loss_ = loss_object(real, pred)

    mask = tf.cast(mask, dtype=loss_.dtype)
    loss_ *= mask

    return tf.reduce_mean(loss_)

def accuracy_function(real, pred):
    mask = tf.math.logical_not(tf.math.equal(real, vocab[vocab.padding_token]))
    mask = tf.expand_dims(tf.cast(mask, dtype=pred.dtype), axis=-1)
    pred *= mask
    acc = train_accuracy(real, pred)

    return tf.reduce_mean(acc)


def excel_preprocessing():
    # 수정필요
    excel_path = '../data/ai_cms_content_한의원.xlsx'
    df = pd.read_excel(excel_path)

    result_dict = {}
    id_df = df['id']
    type_df = df['content_type'].replace(['언론보도', '바이럴'], ['press', 'viral'])

    for i in range(len(df)):
        result_dict[id_df[i]] = type_df[i]

    return result_dict

def main(BATCH_SIZE, MAX_LEN, NUM_EPOCHS, LOAD_MODEL_PATH, data_path):
    gpt_model = GPT2Model(LOAD_MODEL_PATH)

    type_dict = excel_preprocessing()

    seperated_contents = pd.read_excel(data_path) #main 에서 읽어옴
    viral_sents = []
    press_sents = []
    for i in range(len(seperated_contents)):
        content = seperated_contents['sentense'][i]
        if type(content) is float or len(content) < 12 or content[0].isdigit():
            continue

        conent_id = seperated_contents['id'][i]
        if type_dict[conent_id] == 'viral':
            viral_sents.append(content)
        else:
            press_sents.append(content)

    #두가지 Content_type 에 대한 학습시작
    DATA_OUT_PATH = './model'
    viral_model = 'viral_model' #바이럴 모델
    press_model = 'press_model' #언론 보도 모델
    for sents in (viral_sents, press_sents):
        input_data, output_data = sentense_processing(sents, MAX_LEN)

        gpt_model.compile(loss=loss_function,
                          optimizer=tf.keras.optimizers.Adam(1e-4),
                          metrics=[accuracy_function])

        history = gpt_model.fit(input_data, output_data,
                                batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
                                validation_split=0.1)

        if sents == viral_sents:
            save_path = os.path.join(DATA_OUT_PATH, viral_model)
        else:
            save_path = os.path.join(DATA_OUT_PATH, press_model)

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        gpt_model.gpt2.save_pretrained(save_path)




def clean_text(sent):
    sent_clean = re.sub("[^가-힣ㄱ-ㅎㅏ-ㅣ\\s]", "", sent)
    return sent_clean

def translateTextToToken(text):
    SENT_MAX_LEN = 39
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

def train_model_posneg():
    BATCH_SIZE = 32
    NUM_EPOCHS = 3
    VALID_SPLIT = 0.1
    SENT_MAX_LEN = 39

    DATA_IN_PATH = './service/data/'
    DATA_OUT_PATH = './service/data/out'


    DATA_TRAIN_PATH = os.path.join(DATA_IN_PATH, "PosNeg_naver/", "ratings_train.txt")

    train_data = pd.read_csv(DATA_TRAIN_PATH, header = 0, delimiter = '\t', quoting = 3)

    train_data = train_data.dropna()
    train_data.head()

    print("Total # dataset: train - {}".format(len(train_data)))


    train_data_sents = []
    train_data_labels = []

    try:
        for train_sent, train_label in train_data[['document', 'label']].values:
            train_tokenized_text = vocab[tokenizer(clean_text(train_sent))]

            tokens = [vocab[vocab.bos_token]]
            tokens += pad_sequences([train_tokenized_text],
                                    SENT_MAX_LEN,
                                    value=vocab[vocab.padding_token],
                                    padding='post').tolist()[0]
            tokens += [vocab[vocab.eos_token]]

            train_data_sents.append(tokens)
            train_data_labels.append(train_label)
    except:
        print('failed tokenizing')
        return False

    train_data_sents = np.array(train_data_sents, dtype=np.int64)
    train_data_labels = np.array(train_data_labels, dtype=np.int64)

    BASE_MODEL_PATH = './service/finetuning_model/detailed_classification_model/gpt_ckpt'

    cls_model = TFGPT2Classifier(dir_path=BASE_MODEL_PATH, num_class=2)

    optimizer = tf.keras.optimizers.Adam(learning_rate=6.25e-5)
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
    cls_model.compile(optimizer=optimizer, loss=loss, metrics=[metric])

    print('학습 시작')
    try:
        history = cls_model.fit(train_data_sents, train_data_labels,
                                epochs=NUM_EPOCHS,
                                batch_size=BATCH_SIZE,
                                validation_split=VALID_SPLIT)

        weightPath = './service/data/out/posneg/'
        cls_model.save_weights(weightPath, save_format='tf')
        text = "아 더빙.. 진짜 짜증나네요 목소리"

        token_list = translateTextToToken(text)

        origin_result = cls_model.predict(token_list)
        results = tf.argmax(origin_result, axis=1)
        print('원본 : ', origin_result, ' => ', results)
        return True
    except:
        print('failed fit or save')
        return False


def train_model_detail():
    BATCH_SIZE = 32
    NUM_EPOCHS = 3
    VALID_SPLIT = 0.1
    SENT_MAX_LEN = 39

    DATA_IN_PATH = './service/data/'
    DATA_OUT_PATH = './service/data/out'


    DATA_TRAIN_PATH = os.path.join(DATA_IN_PATH, "Training/", "training_data.csv")

    train_data = pd.read_csv(DATA_TRAIN_PATH, header=0)

    # train_data['label'] = train_data['label'].str.encode('utf-8')
    # train_data['sentence'] = train_data['sentence'].str.encode('utf-8')

    train_data.rename(columns={'sentence': 'document'}, inplace=True)
    train_data = train_data.dropna()
    train_data.head()

    # label : 기쁨 : 0, 불안 : 1, 당황 : 2, 슬픔 : 3, 분노 : 4, 상처 : 5
    train_data['label'] = train_data['label'].replace("기쁨", 0)
    train_data['label'] = train_data['label'].replace("불안", 1)
    train_data['label'] = train_data['label'].replace("당황", 2)
    train_data['label'] = train_data['label'].replace("슬픔", 3)
    train_data['label'] = train_data['label'].replace("분노", 4)
    train_data['label'] = train_data['label'].replace("상처", 5)

    # train_data = train_data[0:50]

    print("Total # dataset: train - {}".format(len(train_data)))

    train_data.head()

    train_data_sents = []
    train_data_labels = []

    try:
        for train_sent, train_label in train_data[['document', 'label']].values:
            train_tokenized_text = vocab[tokenizer(clean_text(train_sent))]

            tokens = [vocab[vocab.bos_token]]
            tokens += pad_sequences([train_tokenized_text],
                                    SENT_MAX_LEN,
                                    value=vocab[vocab.padding_token],
                                    padding='post').tolist()[0]
            tokens += [vocab[vocab.eos_token]]

            train_data_sents.append(tokens)
            train_data_labels.append(train_label)
    except:
        print('failed tokenizing')
        return False

    train_data_sents = np.array(train_data_sents, dtype=np.int64)
    train_data_labels = np.array(train_data_labels, dtype=np.int64)

    BASE_MODEL_PATH = './service/finetuning_model/detailed_classification_model/gpt_ckpt'

    cls_model = TFGPT2Classifier(dir_path=BASE_MODEL_PATH, num_class=6)

    optimizer = tf.keras.optimizers.Adam(learning_rate=6.25e-5)
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    metric = tf.keras.metrics.SparseCategoricalAccuracy('accuracy')
    cls_model.compile(optimizer=optimizer, loss=loss, metrics=[metric])

    print('학습 시작')
    try:
        history = cls_model.fit(train_data_sents, train_data_labels,
                                epochs=NUM_EPOCHS,
                                batch_size=BATCH_SIZE,
                                validation_split=VALID_SPLIT)

        weightPath = './service/data/out/save/'
        cls_model.save_weights(weightPath, save_format='tf')
        text = "너무 슬퍼요 눈물나요"
        token_list = translateTextToToken(text)


        origin_result = cls_model.predict(token_list, batch_size=1024)
        results = tf.argmax(origin_result, axis=1)
        print('원본 : ', origin_result, ' => ', results)
        return True
    except:
        print('failed fit or save')
        return False
