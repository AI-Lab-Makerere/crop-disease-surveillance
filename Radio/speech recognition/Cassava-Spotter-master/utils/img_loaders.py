import os
import numpy as np

from PIL import Image, ImageOps
from random import choice, randrange

def load_image( infilename ) :
    target_size = (100, 32) # w H
    img = Image.open( infilename )
    img = ImageOps.fit(img, target_size, Image.ANTIALIAS)
    img = img.convert("RGB")
    img.load()
    img = np.asarray(img, dtype=np.float32) / 255
    img = img[:, :, :3]
    return img

def loadimgs(path='/content/nlp_keyword_bucket/train_1/',n = 0):
    '''
    path => Path of train directory or test directory
    '''
    X=[]
    y = []
    cat_dict = {}
    word_dict = {}
    curr_y = n
    
    # we load every alphabet seperately so we can isolate them later
    for word in os.listdir(path):
        print("loading word: " + word)
        word_dict[word] = curr_y
        word_path = os.path.join(path,word)
        cat_dict[curr_y] = word
        category_images=[]
        
        # read all the images in the current category
        for filename in os.listdir(word_path):
            if filename.split(".")[1] != "png":
                continue
            image_path = os.path.join(word_path, filename)
            image = load_image(image_path)
            if image.shape != (32,100,3):
              print(image.shape)
            category_images.append(image)
            y.append(curr_y)
        try:
            X.append(np.stack(category_images))
        # edge case  - last one
        except ValueError as e:
            print(e)
            print("error - category_images:", category_images)
        curr_y += 1
        #lang_dict[alphabet][1] = curr_y - 1
    y = np.asarray(y)
    X = np.asarray(X)
    return X,y, word_dict


import cv2
import numpy as np

def resize_and_color_image( img, target_size = (100, 32) ) :
    if img.dtype != "float32":
      img = np.float32(img)
    img = cv2.resize(img, target_size, Image.ANTIALIAS)
    if len(img.shape) != 3:
      img = cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
    return img

def make_image_oneshot_task(image_to_oneshot_predict, Xtrain):
    """Create pairs of test image, support set for testing N way one-shot learning. """
    #categories = word_dict_train.keys()
    
    #n_examples #what about this? category by category like before
    #w, h, channels = image_to_oneshot_predict.shape

    # Do I need to assert these 2 are the same or would the CNN deal with
    # preprocessing and resizing ?
    # It won't, I should add a conditional statement to resize
    #  
    w, h, channels = Xtrain[0][0].shape
    
    n_classes = Xtrain.shape[0]
    
    # initialize 2 empty arrays for the input image batch
    pairs=[np.zeros((n_classes, w, h, channels)) for i in range(2)]


    for class_to_compare in range(n_classes):
        #category = categories[i]
        #print(image_to_oneshot_predict.shape)
        image_to_oneshot_predict = resize_and_color_image(image_to_oneshot_predict, (100, 32))
        pairs[0][class_to_compare,:,:,:] = image_to_oneshot_predict # Would this 
        idx_2 = rng.randint(0, len(Xtrain[class_to_compare]))
        #print(Xtrain[class_to_compare][idx_2].shape)
        pairs[1][class_to_compare,:,:,:] = Xtrain[class_to_compare][idx_2].reshape( w, h, channels)
    
    return pairs


