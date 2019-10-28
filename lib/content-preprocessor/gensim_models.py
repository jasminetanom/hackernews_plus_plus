from gensim.models import CoherenceModel, LdaModel, LsiModel, HdpModel, LdaMulticore, TfidfModel

def train_and_save_gensim_model(model_type_str, corpus, dct, file_name='model_300.model', num_topics=None):
    if model_type_str == "lsi":
        model = LsiModel(corpus=corpus, num_topics=num_topics, id2word=dct)
    elif model_type_str == "lda":
        model = LdaModel(corpus=corpus, alpha='auto', num_topics=num_topics, id2word=dct)
    elif model_type_str == "hdp":
        model = HdpModel(corpus=corpus, id2word=dct)
    model.save(file_name)
    return model
