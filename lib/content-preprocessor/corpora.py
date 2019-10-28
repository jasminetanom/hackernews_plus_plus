from gensim.corpora import Dictionary, MmCorpus

def train_dictionary(tokens):
    dct = Dictionary(tokens)
    dct.filter_extremes(no_below=10, no_above=0.3, keep_n=None) # Filter dictionary (valid terms in bag of words/corpus)
    dct.save('dct.dict')
    return dct

def save_corpus(file_name, corpus):
    MmCorpus.serialize(file_name, corpus)
