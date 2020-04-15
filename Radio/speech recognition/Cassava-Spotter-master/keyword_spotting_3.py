# -*- coding: utf-8 -*-
"""Keyword_Spotting_3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I9jZcMsBm32yC9V8GreXm3x2s8jKCyFi
"""

#!gcloud auth login

#!gcloud config set project malaria-detect

#!mkdir data

#!gsutil -m cp -R gs://nlp_keyword_bucket ./data/

#!clear

import os
from utils.processor_class import DataProcessor

## Some preparation code

processor = DataProcessor("data/nlp_keyword_bucket/train_1/", 
            "data/nlp_keyword_bucket/val_1/",
            "data/nlp_keyword_bucket/test_1/")
processor.convert_ogg2wav()


#########################################################################################################
# BEGINNING OF GENERATING SPECTROGRAM IMAGES FOR WAV FILES
######################################################################################################### 

processor.generate_dir_spectograms()

#########################################################################################################
# END OF GENERATING SPECTROGRAM IMAGES FOR WAV FILES
######################################################################################################### 


#########################################################################################################
# BEGINNING OF GENERATING TRAIN VAL TEST SPLIT
# ADD ABILITY TO GENERATE FROM BIG MIXED FOLDER FOR K FOLD CROSS VALIDATION
# ADD K FOLD CROSS VALIDATION
#########################################################################################################

#from sklearn.model_selection import train_test_split
from utils.img_loaders import loadimgs

Xtrain, ytrain, word_dict_train = loadimgs(path='data/nlp_keyword_bucket/train_1/')
Xval, yval, word_dict_val = loadimgs(path='data/nlp_keyword_bucket/val_1/')
Xtest, ytest, word_dict_test = loadimgs(path='data/nlp_keyword_bucket/test_1/')


#########################################################################################################
# END OF GENERATING TRAIN VAL TEST SPLIT
#########################################################################################################

from utils.model_loaders import TeacherModelLoader
teacher_model_loader = TeacherModelLoader(Xtrain, Xval, Xtest,(32,100,3))
teacher_model_loader.get_model()

from keras.models import load_model
# If loading an existing model
#teacher_model_loader.model_to_use = load_model('gdrive/My Drive/best_siamese.h5')

#########################################################################################################
# BEGGINING OF SIAMESE TEACHER TRAINING
#########################################################################################################

teacher_model_loader.train_model()


#########################################################################################################
# END OF SIAMESE TEACHER TRAINING
#########################################################################################################

#########################################################################################################
# BEGGINING OF EVALUATING SIAMESE MODEL
#########################################################################################################

teacher_model_loader.evaluate_model()

#########################################################################################################
# END OF EVALUATING SIAMESE MODEL
#########################################################################################################

#########################################################################################################
# BEGGINING OF TESTING SIAMESE TEACHER ON CONTINOUS STREAM
#########################################################################################################

#S_DB.dtype
gen_of_cut_up_arr = big_bad_generator_for_one_shot_tasks_from_cut_ups(S_DB, Xtrain,None)
list_of_cut_up_arr_lists = generate_window_walks(S_DB)

print(6614912/sr/60)
list_of_cut_up_sounds_lists = generate_window_walks(S_DB)

total_count = 0
for list_arr in list_of_cut_up_arr_lists:
  total_count += len(list_arr)
print(total_count)


big_bad_generataar =  GeneratorClass(radio_show, S_DB, Xtrain, sr, total_count , word_dict_train)
bbg = big_bad_generataar.__iter__()

big_bad_gen = big_bad_generator_for_one_shot_tasks_from_cut_ups(S_DB, Xtrain, None)

big_bad_gen = big_bad_generator_for_one_shot_tasks_from_cut_ups(S_DB, Xtrain, None)

prediction_of_one_shot_baby = teacher_model_loader.model_to_use.predict_generator(bbg, 100, verbose=1)#total_count



#########################################################################################################
# END OF TESTING SIAMESE TEACHER ON CONTINOUS STREAM
#########################################################################################################

#########################################################################################################
# BEGGINING OF GENERATING STUDENT TRAINING PREDICTIONS
#########################################################################################################

preds_of_siamese, xtest_preds_of_siamese = teacher_model_loader.gen_student_preds()

#########################################################################################################
# END OF GENERATING STUDENT TRAINING PREDICTIONS
#########################################################################################################

from utils.model_loaders import StudentModelLoader

student_model_loader = StudentModelLoader(preds_of_siamese, xtest_preds_of_siamese, input_shape = (128,128,3) )
student_model_loader.get_model()


#########################################################################################################
# BEGGINING OF STUDENT DISTILLATION TRAINING
#########################################################################################################


student_model_loader.train_model()
#########################################################################################################
# END OF STUDENT DISTILLATION TRAINING
#########################################################################################################

#########################################################################################################
# BEGINNING OF STUDENT DISTILLATION TESTING
#########################################################################################################

from utils.generators import get_batch_test_distillation, find_maximum_distill_N_top_values

images, targets = get_batch_test_distillation(teacher_model_loader.Xtest)

predicted_targets = student_model_loader.model_to_use.predict(images, batch_size=32, verbose=1)

max_pred_vals = find_maximum_distill_N_top_values(Xtest, predicted_targets)

from sklearn.metrics import classification_report
# import json
CLASS_REPORT_SIAM = classification_report(max_pred_vals_siamese, max_pred_vals)

print(CLASS_REPORT_SIAM)

#########################################################################################################
# END OF STUDENT DISTILLATION TESTING
#########################################################################################################


