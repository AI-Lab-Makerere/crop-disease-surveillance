
from random import randint
import numpy as np

def _get_distillation_batch(preds, batch_size=32):
  main_img_arr = np.empty((32,128,128,3), float)
  main_preds_arr = np.empty((32,165), float)
  for batch_idx in range(batch_size):
    for arr_idx in range(len(preds)):
      img_to_predict, arr_of_sigmoids = preds[arr_idx]
      img_to_predict = np.asarray(img_to_predict)
      img_to_predict = cv2.resize(img_to_predict, (128, 128), interpolation = cv2.INTER_AREA) 
      arr_of_sigmoids = np.asarray(arr_of_sigmoids).reshape(165)
     
    main_img_arr[batch_idx, :, :, :] = img_to_predict
    main_preds_arr[batch_idx, :] = arr_of_sigmoids

  return (main_img_arr, main_preds_arr)

def find_maximum_distill_N_top_values(X, predictions, threshold = 0.0, N = 1):

    predicted_max_targets = []
  
    key_word_count = X.shape[0]
    #replace 165 with len(Xtrain)
    total_count = len(predictions)
    for one_shot_set in predictions:
        # print("Counter Value: " + str(counter))
        arr_max_index = np.argmax(np.abs(one_shot_set), axis=0)
        # print("Arr max index: " + str(arr_max_index))
        # print("Hit index: " + str(counter*key_word_count + arr_max_index) )
        # print("Hit Value: " + str(predictions[counter*key_word_count + arr_max_index]) ) 
        # print("Hit Random Assurance: " + str(predictions[counter*key_word_count + randint(0,key_word_count-1)]))
        #if predictions[( counter*key_word_count + arr_max_index)] > threshold:
      #We have a hit
        predicted_max_targets.append(  arr_max_index )

    return predicted_max_targets

 

def distillation_generator(preds, batch_size=32):
    #input Xtrain, siamese_model
    # input image and Siamese model predictions as targets
    
  while True:
    pair_to_return = _get_distillation_batch(preds, batch_size=32)
    yield pair_to_return



import numpy.random as rng
import cv2
def get_batch_test_distillation(X, categories = None, reshape_size= (128, 128), resize=True):
  n_classes = X.shape[0]
  if reshape_size != None:
    w = reshape_size[0]
    h = reshape_size[1]
    channels = 3
  else:
    w, h, channels = X[0][0].shape

  sum_of_images = 0
  for category_idx in range(X.shape[0]):
      sum_of_images += X[category_idx].shape[0]
  #categories = rng.choice(n_classes,size=(batch_size,),replace=False)
  images=[np.zeros((sum_of_images, w, h, channels))]
  targets=[np.zeros((sum_of_images))]
  counter = 0

  for category_idx in range(X.shape[0]):
    print(category_idx)
    for image_idx in range(X[category_idx].shape[0]):

      #category = categories[image_idx]
      image = X[category_idx][image_idx]
      if resize:
        image = cv2.resize(image, reshape_size, interpolation = cv2.INTER_AREA)
      images[0][counter] = image
      targets[0][counter] = category_idx
      counter += 1      
        # pick images of same class for 1st half, different for 2nd
  return images, targets


def get_batch(X, categories = None, batch_size= 32,s="train"):
    """
    Create batch of n pairs, half same class, half different class
    """
    #if s == 'train':
    #    X = Xtrain
    #    categories = classes
    #else:
    #    X = Xval
    #    categories = classes
    n_classes = X.shape[0]
    #n_examples
    w, h, channels = X[0][0].shape
    
    # randomly sample several classes to use in the batch
    categories = rng.choice(n_classes,size=(batch_size,),replace=False)
    
    # initialize 2 empty arrays for the input image batch
    pairs=[np.zeros((batch_size, w, h, channels)) for i in range(2)]
    
    # initialize vector for the targets
    targets=np.zeros((batch_size,))
    
    # make one half of it '1's, so 2nd half of batch has same class
    targets[0][batch_size//2:] = 1
    for i in range(batch_size):
        category = categories[i]
        idx_1 = rng.randint(0, len(X[category]))
        pairs[0][i,:,:,:] = X[category][idx_1].reshape(w, h, channels)
         
        # pick images of same class for 1st half, different for 2nd
        if i >= batch_size // 2:
            category_2 = category
            
        else:
            # add a random number to the category modulo n classes to ensure 2nd image has a different category
            category_2 = (category + rng.randint(1,len(X))) % len(X)
        idx_2 = rng.randint(0, len(X[category_2]))
        pairs[1][i,:,:,:] = X[category_2][idx_2].reshape( w, h, channels)
        targets[1] = teacher_model.predict([pairs[0][i], pairs[1][i]])
    # targets[0] == siamese targets --- targets[1] == student_targets
    return pairs, targets

def get_batch_student(X, teacher_model, batch_size= 1500,s="train"):
    """
    Create batch of n pairs, half same class, half different class
    """
    #if s == 'train':
    #    X = Xtrain
    #    categories = classes
    #else:
    #    X = Xval
    #    categories = classes
    n_classes = X.shape[0]
    #n_examples
    w, h, channels = X[0][0].shape
    
    # randomly sample several classes to use in the batch
    #categories = rng.choice(n_classes,size=(batch_size,),replace=False)
    
    # initialize 2 empty arrays for the input image batch
    pairs=[np.zeros((batch_size, w, h, channels)) for i in range(2)]
    
    # initialize vector for the targets
    targets=np.zeros((batch_size,))
    
    # make one half of it '1's, so 2nd half of batch has same class
    targets[batch_size//2:] = 1
    for i in range(batch_size):
        category = rng.randint(0,164)
        idx_1 = rng.randint(0, len(X[category]))
        pairs[0][i,:,:,:] = X[category][idx_1].reshape(w, h, channels)
        
        # pick images of same class for 1st half, different for 2nd
        if i >= batch_size // 2:
            category_2 = category
            
        else:
            # add a random number to the category modulo n classes to ensure 2nd image has a different category
            category_2 = (category + rng.randint(1,len(X))) % len(X)
        idx_2 = rng.randint(0, len(X[category_2]))
        pairs[1][i,:,:,:] = X[category_2][idx_2].reshape( w, h, channels)
    
    return pairs, targets

def generate(X, labels,batch_size=32):
    """a generator for batches, so model.fit_generator can be used. """
    while True:
        pairs, targets = get_batch(X, labels,batch_size)
        yield (pairs, targets)


