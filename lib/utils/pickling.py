import pickle

def save_pickle(file_name, object_to_pickle):
    with open(file_name, 'wb') as f:
        pickle.dump(object_to_pickle, f)

def load_pickle(file_name):
    with open(file_name, 'rb') as f:
        unpickled_object = pickle.load(f)
    return unpickled_object
