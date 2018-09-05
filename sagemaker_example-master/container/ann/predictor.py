# This is the file that implements a flask server to do inferences. It's the
# file that you will modify to implement the scoring for your own algorithm.
from __future__ import print_function

import os
import StringIO
import flask

import tensorflow as tf
import numpy as np
import pandas as pd

from keras import backend as K
from keras.models import load_model
from sklearn.preprocessing import StandardScaler



from sklearn.preprocessing import LabelEncoder, OneHotEncoder


# A singleton for holding the model. This simply loads the model and holds it.
# It has a predict function that does a prediction based on the model and the
# input data.
class ScoringService(object):
    model = None                # Where we keep the model when it's loaded

    @classmethod
    def get_model(cls,by,model):
        """
        Get the model object for this instance,
        loading it if it's not already loaded.
        """
        model_path = os.path.join("s3://diffclass-modelstorage", by)

        if cls.model is None:
            cls.model = load_model(
                os.path.join(model_path, model))
        return cls.model

    @classmethod
    def predict(cls, input):
        """For the input, do the predictions and return them.

        Args:
            input (a pandas dataframe): The data on which to do the
            predictions.

            There will be one prediction per row in the dataframe
        """
        sess = K.get_session()
        with sess.graph.as_default():
            clf = cls.get_model()
            return clf.predict(input)



# The flask app for serving predictions
app = flask.Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """
    Determine if the container is working and healthy.
    In this sample container, we declare it healthy if we can load the model
    successfully.
    """

    # Health check -- You can insert a health check here
    health = ScoringService.get_model() is not None
    status = 200 if health else 404
    return flask.Response(
        response='\n',
        status=status,
        mimetype='application/json')



def peak2vek(peaks,bins=180):
    """
    converts a list of two thetas into a vector of the appropriate size
    """
    blank = np.zeros(bins)

    for peak in peaks:
        blank[int(peak*90.0/bins)] += 1

    return blank


@app.route('/invocations', methods=['POST'])
def transformation():
    """
    Do an inference on a single batch of data. In this sample server, we take
    data as Json, convert it to a nunmpy array for internal use and then
    convert the predictions back to CSV (which really just means one prediction
    per line, since there's a single column.
    """
    data = None

    # Convert from CSV to pandas
    if flask.request.content_type == 'json':
        data = flask.request.get_json
        """
        I'm going to write a method to turn the json into an input of the proper kind
        """
        data = peak2vec(data["peaks"])

    else:
        return flask.Response(
            response='This predictor only supports JSON',
            status=415,
            mimetype='text/plain')

    print('Invoked with {} records'.format(data.shape[0]))

    # Do the prediction
    prediction = ScoringService.predict(data)

    # Convert from numpy back to CSV
    out = StringIO.StringIO()
    pd.DataFrame(prediction).to_csv(out, header=False, index=False)
    result = out.getvalue()

    return flask.Response(response=result, status=200, mimetype='text/csv')
