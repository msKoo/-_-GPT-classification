import json

class KnuSL():
	def __init__(self):
		print('.', end='')

	def data_list(self,wordname):
		with open('sentiment/data/KNU/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
			data = json.load(f)
		result = ['None','None']
		for i in range(0, len(data)):
			if data[i]['word'] == wordname:
				result.pop()
				result.pop()
				result.append(data[i]['word'])
				result.append(data[i]['polarity'])
				break
			# elif data[i]['word_root'] == wordname :
			# 	result.pop()
			# 	result.pop()
			# 	result.append(data[i]['word_root'])
			# 	result.append(data[i]['polarity'])
		
		r_word = result[0]
		s_word = result[1]
							
		return r_word, s_word


def senti_Anal(wordname):
	with open('sentiment/data/KNU/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
		data = json.load(f)
	result = ['None', 'None']
	for i in range(0, len(data)):
		if data[i]['word'] == wordname:
			result.pop()
			result.pop()
			result.append(data[i]['word'])
			result.append(data[i]['polarity'])
			break
	s_word = result[1]

	return s_word