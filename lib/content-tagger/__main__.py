import gensim
from gensim.matutils import corpus2csc
import create_labelled_dataset
sys.path.insert(1, '../utils')
import pickling

lsi_300_corpus = gensim.corpora.MmCorpus('../content-preprocessor/corpus_tfidf.mm')
lsi_300_csc = corpus2csc(lsi_300_corpus)

def train_classifier(corpus, labels):
    lsi_X_train, lsi_X_test, lsi_y_train, lsi_y_test = train_test_split(corpus.T, labels, random_state=42)
    best_clf = LabelPowerset(LinearSVC(C=1.291549665014884, class_weight=None, dual=True,
         fit_intercept=True, intercept_scaling=1, loss='squared_hinge',
         max_iter=1000, multi_class='ovr', penalty='l2', random_state=42,
         tol=0.0001, verbose=0))
    best_clf.fit(lsi_X_train, lsi_y_train)
    return best_clf

labelled_csc_corpus, labels = create_labelled_dataset.get_labelled_csc_corpus()
clf = train_classifier(labelled_csc_corpus, labels)
pickling.save_pickle(clf, 'tagger_model.pkl')
