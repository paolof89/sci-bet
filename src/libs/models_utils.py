from keras.models import model_from_json


def save_model(model, path):
    # serialize model to JSON
    model_json = model.to_json()
    with open(path + '/' + "model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights(path + '/' +"model.h5")
    print("Model saved to disk")

def load_model(path):
    # load json and create model
    json_file = open(path + '/' +'model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    # load weights into new model
    model.load_weights(path + '/' +"model.h5")
    print("Model loaded from disk")
    return model