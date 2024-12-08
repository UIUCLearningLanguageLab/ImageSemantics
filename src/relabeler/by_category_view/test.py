from collections import Counter
import numpy as np

document = "the dogs chased the cat . the cat ran up the tree . the cat hissed at the dogs ."

word_list = document.split()
freq_dict = Counter(word_list)
corpus_type_list = list(freq_dict.keys())
corpus_type_index_dict = dict(zip(corpus_type_list, range(len(corpus_type_list))))
corpus_num_types = len(corpus_type_list)

vocab_list = freq_dict.most_common(8)
inflection_list = ['ED', 'ING', 'S']
inflection_index_dict = dict(zip(inflection_list, range(len(inflection_list))))
num_inflections = len(inflection_list)

verb_root_dict = {'chased': ('chase', 'ED', 1),
                  'ran': ('run', 'ED', 0),
                  'hissed': ('hiss', 'ED', 1),
                  'chasing': ('chase', 'ING', 1),
                  'chase': ('chase', 'ROOT', 1)}

vocab_index_dict = dict(zip(vocab_list, range(len(vocab_list))))
vocab_size = len(vocab_index_dict)

verb_root_list = ['chase', 'ran', 'hiss']
verb_root_index_dict = dict(zip(verb_root_list, range(len(verb_root_list))))
num_verb_roots = len(verb_root_list)

print(vocab_index_dict)
window_size = 3
num_directions = 2

cooc_matrix = np.zeros([num_verb_roots, vocab_size, window_size, num_inflections, num_directions])
# (num_verbs, vocab_size, window_size, 4, 2)

print(cooc_matrix.shape)

for i, word1 in enumerate(word_list):
    if word1 in verb_root_dict:

        verb_root = verb_root_dict[word1][0]
        verb_root_index = verb_root_index_dict[verb_root]

        inflection = verb_root_dict[word1][1]
        regular = verb_root_dict[word1][2]
        inflection_index = inflection_index_dict[inflection]

        forward_window = word_list[i+1:i+1+window_size]
        if i - window_size < 0:
            backward_index = 0
        else:
            backward_index = i - window_size
        backward_window = word_list[backward_index:i]

        for j in range(window_size):  # 103,
            forward_word = forward_window[j]
            if forward_word in vocab_index_dict:
                forward_vocab_index = vocab_index_dict[forward_word]
                cooc_matrix[verb_root_index, forward_vocab_index, j, inflection_index, 0] = 1

            backward_word = backward_window[j]
            if backward_word in vocab_index_dict:
                backward_vocab_index = vocab_index_dict[backward_word]
                cooc_matrix[verb_root_index, backward_vocab_index, j, inflection_index, 1] = 1

print(cooc_matrix)

cooc_matrix_summed_over_verbs = cooc_matrix.sum(axis=0)
cooc_matrix_summed_over_window_size = cooc_matrix.sum(axis=2)

cooc_matrix_summed_over_verbs_and_window_size = cooc_matrix_summed_over_verbs.sum(axis=1)
cooc_matrix_summed_over_verbs_and_window_size_and_direction = cooc_matrix_summed_over_verbs_and_window_size.sum(axis=2)
# (vocab_size, 4)