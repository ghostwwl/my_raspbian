#!/usr/bin/python3
#-*- coding:utf-8 -*-

# ********************************
#    FileName: FaceRecognitionModel.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2019/12/24
#    Note    :
# ********************************

import os
import math
import joblib
from sklearn import svm, neighbors
from util import warp_func_use_time

class FaceRecognitionModel(object):
    def __init__(self, parent, model_path='./model'):
        self.parent = parent
        self.MODEL_PATH = model_path
        self._model = None

    @warp_func_use_time
    def svm_train(self):
        model = svm.SVC(gamma='scale')
        self.parent.loger.info('Start to train svm model...')
        model.fit(self.parent.KNOWN_FACE_ENCODINGS, self.parent.KNOWN_FACE_NAMES)
        self.parent.loger.info('Train svm model [ OK ]')

        if not os.path.exists(self.MODEL_PATH):
            try:
                os.makedirs(self.MODEL_PATH)
            except:
                self.loger.error('mkdirs `{}` err.({})'.format(self.MODEL_PATH, GTraceback()))

        model_file = os.path.join(self.MODEL_PATH, 'recognition_svm.clf')
        joblib.dump(model, model_file)
        self.parent.loger.info('Save svm classifier model [ ok ]')

    def svm_predict(self, face_encoding):
        if self._model is None:
            self._model = joblib.load(os.path.join(self.MODEL_PATH, 'recognition_svm.clf'))

        name = self._model.predict([face_encoding])
        return name

    @warp_func_use_time
    def knn_train(self, n_neighbors=None, knn_algo='ball_tree', verbose=False):
        if n_neighbors is None:
            n_neighbors = int(round(math.sqrt(len(self.parent.KNOWN_FACE_ENCODINGS))))
            if verbose:
                self.parent.loger.info("Chose n_neighbors automatically:", n_neighbors)

        model = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        self.parent.loger.info('Start to train svm model...')
        model.fit(self.parent.KNOWN_FACE_ENCODINGS, self.parent.KNOWN_FACE_NAMES)

        self.parent.loger.info('Train knn model [ OK ]')

        if not os.path.exists(self.MODEL_PATH):
            try:
                os.makedirs(self.MODEL_PATH)
            except:
                self.loger.error('mkdirs `{}` err.({})'.format(self.MODEL_PATH, GTraceback()))

        model_file = os.path.join(self.MODEL_PATH, 'recognition_knn.clf')
        joblib.dump(model, model_file)
        self.parent.loger.info('Save knn classifier model [ ok ]')

    def knn_predict(self, face_encoding):
        if self._model is None:
            self._model = joblib.load(os.path.join(self.MODEL_PATH, 'recognition_knn.clf'))

        return self._model.predict([face_encoding])


if __name__ == '__main__':
    pass