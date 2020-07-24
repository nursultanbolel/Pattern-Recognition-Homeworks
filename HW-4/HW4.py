from sklearn.datasets import load_files       
from keras.utils import np_utils
import numpy as np
from glob import glob
import matplotlib.pyplot as plt 
from tqdm import tqdm
from keras.preprocessing import image  
from PIL import ImageFile     
from sklearn.metrics import classification_report,accuracy_score
from skimage.feature import hog
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC

#################################################################
# define function to load train, test, and validation datasets
def load_dataset(path):
    data = load_files(path)
    condition_files = np.array(data['filenames'])
    print(len(condition_files))
    #condition_targets = np_utils.to_categorical(np.array(data['target']), 15)
    condition_targets = np_utils.to_categorical(np.array(data['target']), 15)
    return condition_files, condition_targets

# load train, test, and validation datasets
path_org = 'data/'
train_files, y_train = load_dataset(path_org+'train')
valid_files, valid_targets = load_dataset(path_org+'val')
test_files, y_test = load_dataset(path_org+'/test')

# load list of labels
condition_names = [item[20:-1] for item in sorted(glob(path_org+'train/*/'))]
print (condition_names)
# print statistics about the dataset
print('There are %d total categories.' % len(condition_names))
print('There are %s total images.\n' % len(np.hstack([train_files, valid_files, test_files])))
print('There are %d training images.' % len(train_files))
print('There are %d validation images.' % len(valid_files))
print('There are %d test images.'% len(test_files))

def path_to_tensor(img_path):
    # loads RGB image as PIL.Image.Image type
    img = image.load_img(img_path, target_size=(128, 128))
    # convert PIL.Image.Image type to 3D tensor with shape (32, 32, 3)
    x = image.img_to_array(img)
    x = x.reshape(-1,49152)
    
    return  x

#################################################################
def paths_to_tensor(img_paths):
    list_of_tensors = [path_to_tensor(img_path) for img_path in tqdm(img_paths)]
    return np.vstack(list_of_tensors)



#################################################################
#read images 
                      
ImageFile.LOAD_TRUNCATED_IMAGES = True                 
# pre-process the data for Keras
x_train = paths_to_tensor(train_files).astype('float32')
#valid_tensors = paths_to_tensor(valid_files).astype('float32')
x_test = paths_to_tensor(test_files).astype('float32')

y_train = y_train.argmax(1)
y_test = y_test.argmax(1)


#feature extraction function
#Extract Hog Features.

def extractFeatures(data):
    
    features = np.zeros( (data.shape[0],512), np.float32)

    #I used hog function to extract some meaningful features from image.
    #All image in data are used as a parameter in hog function
    #data includes images as vector, I converted this vectors to (128*128*3) format to use in hog function
    #hog function returns feature and output hog image
    #features is saved in features array
    
    w,h = data.shape;
    for i in range (w):
        image = np.reshape(data[i,:], (128,128,3))
        features[i] ,hog_image = hog(image, orientations=8, pixels_per_cell=(16,16), cells_per_block=(8, 8), block_norm= 'L2',visualize=True)
    #returns features array
    return features

#Training function of SVM
# find svm models that holds hyperplanes  as w1, w2, w3, ...., w15
def trainClassifier(x_train, y_train):
    
    #train and return SVM model
    #we are assumed that svm_model is the trained SVM model

    #I used OneVsTestClassifier() function which is in sklearn to have 15 hyperlanes.
    svm_model = OneVsRestClassifier(SVC()).fit(x_train, y_train)    
    
    return svm_model

#Prediction function of SVM
def predictClassifier(svm_model, x_test):
    
    #find predictions by using SVM model
    y_pred = svm_model.predict(x_test)

    return y_pred

#################################################################  

#step1: feature extraction for train data
x_train_features = extractFeatures(x_train)  

#step2: feature extraction for test data
x_test_features = extractFeatures(x_test)
  
#step3: train SVM model
svm_model = trainClassifier(x_train_features, y_train)

#step4: make predictions           
          
y_pred = predictClassifier(svm_model, x_test_features)
     
#step5: compute accuracy  
            
print('Accuracy: '+str(accuracy_score(y_test, y_pred)) )
print('\n')
print(classification_report(y_test, y_pred)) 


#step6: make prediction for sample test
sample_test = x_test[0]    
plt.imshow(np.int8(sample_test).reshape(128,128,3))
plt.show()


sample_test = np.reshape(sample_test, (1,sample_test.shape[0]))

sample_test_features = extractFeatures(sample_test) 
y_pred_sample_test = predictClassifier(svm_model, sample_test_features)

print('class label of test sample is:',y_pred_sample_test)

