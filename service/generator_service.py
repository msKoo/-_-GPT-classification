import os
import tensorflow as tf
from service.finetuning_model.train_module import GPT2Model, tokenizer, vocab, tf_top_k_top_p_filtering
from service.cosine_similarity import getSimilarity


def generate_sent(seed_word, model, max_step=100, greedy=False, top_k=0, top_p=0.):
    sent = seed_word
    toked = tokenizer(sent)
    for _ in range(max_step):
        input_ids = tf.constant([vocab[vocab.bos_token],]  + vocab[toked])[None, :]
        outputs = model(input_ids)[:, -1, :]
        if greedy:
            gen = vocab.to_tokens(tf.argmax(outputs, axis=-1).numpy().tolist()[0])
        else:
            output_logit = tf_top_k_top_p_filtering(outputs[0], top_k=top_k, top_p=top_p)
            gen = vocab.to_tokens(tf.random.categorical(output_logit, 1).numpy().tolist()[0])[0]
        if gen == '</s>':
            break
        sent += gen.replace('▁', ' ')
        toked = tokenizer(sent)
    return sent

def text_gen():

    finetuning_model_path = './service/finetuning_model'
    press_model_name = 'press_model'
    viral_model_name = 'viral_model'

    press_save_path = os.path.join(finetuning_model_path, press_model_name)
    viral_save_path = os.path.join(finetuning_model_path, viral_model_name)

    press_gpt_model = GPT2Model(press_save_path)
    viral_gpt_moel = GPT2Model(viral_save_path)


    keyword = '한의원'
    generate_p = generate_sent(keyword, press_gpt_model, top_k=0, top_p=0.95)
    generate_v = generate_sent(keyword, viral_gpt_moel, top_k=0, top_p=0.95)

    print("언론보도 : ", generate_p)
    print("바이럴 : ", generate_v)
    return

def request_body(keyword, type):
    result = {}
    finetuning_model_path = './service/finetuning_model'
    model_name = type + "_model"

    model_save_path = os.path.join(finetuning_model_path, model_name)
    model = GPT2Model(model_save_path)

    generate_text = generate_sent(keyword, model, top_k=0, top_p=0.95)
    result['generated_text'] = generate_text

    #cosine 유사도
    cosinResult = getSimilarity(generate_text)
    result['cosin'] = cosinResult

    return result



