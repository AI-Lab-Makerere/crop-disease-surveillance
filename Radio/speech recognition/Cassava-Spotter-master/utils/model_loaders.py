
import numpy as np

from keras.layers import Input, Conv2D, Dense, MaxPooling2D, Lambda, Flatten
from keras.models import Sequential, Model
from keras.regularizers import l2
from keras.applications import Xception, ResNet50V2, MobileNetV2
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.losses import binary_crossentropy
from copy import deepcopy
from keras import backend as K

from .generators import generate, lazy_generate
from .img_loaders import make_image_oneshot_task

def my_binary_crossentropy(y_true, y_pred):
    return binary_crossentropy(y_true, y_pred, from_logits=True)

class TeacherModelLoader():

    def __init__(self,Xtrain, Xval, Xtest, input_shape, conv_base = None):
        self.input_shape = input_shape
        self.conv_base = conv_base
        self.Xtrain = Xtrain
        self.Xval = Xval
        self.Xtest = Xtest

    @staticmethod
    def initialize_weights(shape, name=None):
        """
            The paper, http://www.cs.utoronto.ca/~gkoch/files/msc-thesis.pdf
            suggests to initialize CNN layer weights with mean as 0.0 and standard deviation of 0.01
        """
        return np.random.normal(loc = 0.0, scale = 1e-2, size = shape)

    @staticmethod  
    def initialize_bias(shape, name=None):
        """
            The paper, http://www.cs.utoronto.ca/~gkoch/files/msc-thesis.pdf
            suggests to initialize CNN layer bias with mean as 0.5 and standard deviation of 0.01
        """
        return np.random.normal(loc = 0.5, scale = 1e-2, size = shape)


    def get_model(self):
        """
            Model architecture
        """
        if self.conv_base:
            self.conv_base = self.conv_base(include_top=False, input_tensor=None, input_shape=self.input_shape, pooling=None, classes=None)
        else:
            self.conv_base = ResNet50V2(include_top=False, input_tensor=None, input_shape=self.input_shape, pooling=None, classes=None) #rebuild on change)
        
        # Define the tensors for the two input images
        left_input = Input(self.input_shape)
        right_input = Input(self.input_shape)
        
        # Convolutional Neural Network
        
        encoded_l = self.conv_base(left_input)
        encoded_r = self.conv_base(right_input)
        
        flatten = Flatten()
        dense = Dense(4096)
        
        flattened_l = flatten(encoded_l)
        flattened_r = flatten(encoded_r)
        dense_l = dense(flattened_l)
        dense_r = dense(flattened_r)
        
        
        # Add a customized layer to compute the absolute difference between the encodings
        
        L1_layer = Lambda(lambda tensors:K.abs(tensors[0] - tensors[1]))
        L1_distance = L1_layer([dense_l, dense_r])
        
        # Add a dense layer with a sigmoid unit to generate the similarity score
        prediction = Dense(1)(L1_distance)#,activation='sigmoid')
                           #,
                           #bias_initializer=initialize_bias)
            
        
        # Connect the inputs with the outputs
        self.model_to_use = Model(inputs=[left_input,right_input],outputs=prediction)
        
        # return the model
        #self.siamese_net

    def train_model(self,best_model_save_path = 'best_siamese.h5', command_dataset=False, **kwargs):

        adam = Adam(lr=0.00005)
        stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=30, verbose=1, mode='min', baseline=None, restore_best_weights=True)
        filepath="model-improvement-{epoch:03d}-{val_loss:.5f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor="val_loss", save_best_only=True, verbose=1)

        callbacks = [
            stopping
            #,
            #checkpoint
        ]
        Xtrain = deepcopy(self.Xtrain)
        Xval = deepcopy(self.Xval)
        self.model_to_use.compile(loss=my_binary_crossentropy, optimizer=adam, metrics=['accuracy'])
        if command_dataset:
                    
            self.history = self.model_to_use.fit_generator(lazy_generate(kwargs["root_dir"],kwargs["training_list"]
        ,kwargs["batch_size"], kwargs["whitelist"]),use_multiprocessing=False, steps_per_epoch=32, epochs=200, validation_data=lazy_generate(kwargs["root_dir"],
            kwargs["validation_list"],kwargs["batch_size"], 
            kwargs["whitelist"]),validation_steps=100, callbacks=callbacks)
        else:        
            self.history = self.model_to_use.fit_generator(generate(Xtrain,None,32),use_multiprocessing=False, steps_per_epoch=32, epochs=200, 
                                    validation_data=generate(self.Xval,None,32),validation_steps=100, callbacks=callbacks)

        self.model_to_use.save(best_model_save_path)#'best_siamese.h5')

    def evaluate_model(self):
        test = generate(self.Xtest, 1000)
        test_generator = generate(self.Xtest, None, 164)
        pairs, labels =  test_generator.__next__()
        print(self.model_to_use.evaluate(pairs, labels))


    def gen_student_preds(self):

        preds_of_siamese = []
        from random import randint
        for word_idx in range(len(self.Xtrain)):
          print(word_idx)
          for img_idx in range(self.Xtrain[word_idx].shape[0]):
            #keyword_to_predict = randint(0, len(Xtrain)-1)
            #spectrogram_to_predict = randint(0, Xtrain[keyword_to_predict].shape[0]-1)
            img_to_predict = self.Xtrain[word_idx][img_idx]
            teacher_model_prediction_pairs = make_image_oneshot_task(img_to_predict, self.Xtrain)
            arr_of_sigmoids = np.asarray( self.model_to_use.predict(teacher_model_prediction_pairs, verbose=1) )
            preds_of_siamese.append( (img_to_predict, arr_of_sigmoids) )

        xtest_preds_of_siamese = []
        for word_idx in range(len(self.Xtest)):
          print(word_idx)
          for img_idx in range(self.Xtest[word_idx].shape[0]):
            #keyword_to_predict = randint(0, len(Xtrain)-1)
            #spectrogram_to_predict = randint(0, Xtrain[keyword_to_predict].shape[0]-1)
            img_to_predict =self.Xtest[word_idx][img_idx]
            teacher_model_prediction_pairs = make_image_oneshot_task(img_to_predict, self.Xtest)
            arr_of_sigmoids = np.asarray( self.model_to_use.predict(teacher_model_prediction_pairs, verbose=1) )
            xtest_preds_of_siamese.append( (img_to_predict, arr_of_sigmoids) )

        return preds_of_siamese, xtest_preds_of_siamese



class StudentModelLoader(TeacherModelLoader):
    
    def __init__(self, shape, conv_base = None, classes=165):
        self.shape = shape
        self.input_shape = shape[1:]
        self.conv_base = conv_base
        self.classes = classes
        #self.preds_of_siamese = preds_of_siamese
        #self.Xval = Xval
        #self.xtest_preds_of_siamese = xtest_preds_of_siamese
        #How did we call a super class call again?        

    def get_model(self):
        
        if self.conv_base:
            self.conv_base = self.conv_base(include_top=False, input_tensor=None, input_shape=self.input_shape, pooling=None, classes=None)
        else:        
            self.conv_base = MobileNetV2(include_top=False, input_tensor=None, input_shape=self.input_shape, pooling=None, classes=None) #rebuild on change)    
        
        input_tensor = Input(shape=self.input_shape)

        encoded = self.conv_base(input_tensor)

        flatten_layer = Flatten()
        
        flattened = flatten_layer(encoded)

        dense_layer = Dense(512)

        densed_tensor = dense_layer(flattened)

        #L1_layer = Lambda(lambda tensors:K.abs(tensors[0] - tensors[1]))
        #difference_tensor = L1_layer([densed_right_tensor, densed_left_tensor])
        
        # Add a dense layer with a sigmoid unit to generate the similarity score
        prediction = Dense(self.classes)(densed_tensor)
                           #,
                           #bias_initializer=initialize_bias)  
        self.model_to_use = Model(inputs=input_tensor,outputs=prediction)
        

    def train_model(self, preds_of_siamese, save_dir='best_student.h5'):

        adam = Adam(lr=0.00005)
        stopping = EarlyStopping(monitor='val_mean_squared_error', min_delta=0, patience=50, verbose=1, mode='auto', baseline=None, restore_best_weights=True)


        filepath="model-improvement-{epoch:02d}-{mean_squared_error:.8f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor="val_mean_squared_error", period=200, verbose=1)

        callbacks = [
            stopping
            ,
            checkpoint
        ]


        self.model_to_use.compile(loss='mse', optimizer=adam, metrics=['mae', "mse"])
        #student_model.fit_generator(distillation_generator(preds_of_siamese), steps_per_epoch=5, epochs=1426 ,callbacks=callbacks,validation_data=distillation_generator(xval_preds_of_siamese),validation_steps=4, verbose=1)
        self.model_to_use.fit(x=preds_of_siamese[0], y=preds_of_siamese[1], batch_size=32,
        #validation_data=xval_preds_of_siamese, 
        epochs=1426)
        self.model_to_use.save(save_dir)

