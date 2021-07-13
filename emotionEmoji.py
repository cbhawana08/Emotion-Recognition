from keras.models import model_from_json
import numpy as np
import cv2

class FacialExpressionModel(object):
    EMOTIONS_LIST = ["ANGRY", "DISGUST", "FEAR", "HAPPY", "SAD", "SURPRISE", "NEUTRAL"]; ## dont change the order
    def __init__(self, model_json_file, model_weights_file): # __init acts like a constructor
        # load model from JSON file
        with open(model_json_file, "r") as json_file:
            loaded_model_json = json_file.read()
            self.loaded_model = model_from_json(loaded_model_json)

        # load weights into the new model
        self.loaded_model.load_weights(model_weights_file)
        print("Model loaded from disk")
        self.loaded_model.summary()

    def predict_emotion(self, img):
        self.preds = self.loaded_model.predict(img) 
        self.preds[4:6] += 0.1 #List of 6 elements as we are classifying 6 emotions
        self.preds[1:3] += 0.2
        lbl = np.argmax(self.preds) #Returns the index of the element with the highest value
        return FacialExpressionModel.EMOTIONS_LIST[lbl], lbl


rgb = cv2.VideoCapture(0)
facec = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') 
font = cv2.FONT_HERSHEY_SIMPLEX #Font style for the text string on the image
emo_happy = cv2.imread('happy.png',1)
emo_sad = cv2.imread('sad.png',1)
emo_fear = cv2.imread('fear.png',1)
emo_disgust = cv2.imread('disgust.png',1)
emo_surprise = cv2.imread('surprise.png',1)
emo_angry = cv2.imread('angry.png',1)
emo_neutral = cv2.imread('neutral.png',1) # '1' means colored image
emoji = [emo_angry,emo_disgust,emo_fear,emo_happy,emo_sad,emo_surprise,emo_neutral] #fix order

def __get_data__():
    _, fr = rgb.read() #Checks if the frame is read correctly
    gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY) #Converting image to grayscale
    gray = cv2.equalizeHist(gray)   #Pre-processing - application of Histogram equalisation
    faces = facec.detectMultiScale(gray, 1.25, 5) # This returns positions of the rectangles containing the faces
    #2nd and 3rd parameter are scaleFactor and minNeighbors
    return faces, fr, gray

def start_app(cnn):
    skip_frame = 10
    data = []
    flag = False
    emo=None
    while True:
        faces, fr, gray_fr = __get_data__()
        for (x, y, w, h) in faces:
            fc = gray_fr[y:y+h, x:x+w]
            fc = cv2.normalize(fc,None,0,255,cv2.NORM_MINMAX) #Normalise the image 
#             fc = cv2.addWeighted(fc,1.5,blur,-0.5,0)
            roi = cv2.resize(fc, (48, 48)) 
            pred, lbl = cnn.predict_emotion(roi[np.newaxis, :, :, np.newaxis]) #Check exact meaning 
            cv2.putText(fr, pred, (x, y), font, 1, (255, 255, 0), 2)
            cv2.rectangle(fr,(x,y),(x+w,y+h),(255,0,0),2) 
            x1 = x + w//2
            y1 = y + h//2
            emo = emoji[lbl]
            emo = cv2.resize(emo,(h,w))
            fr[y:y+h,x:x+w] = cv2.addWeighted(fr[y:y+h,x:x+w],0.5,emo,0.5,0) #Blending the images to give an effect of transparency

        if cv2.waitKey(1) == 27: # 27 is the ASCII value for the esc key
            cv2.destroyAllWindows()
            break
#         cv2.imshow("img",emo)
        cv2.imshow('Facial Expression Recognition', fr)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    model = FacialExpressionModel("model1.json", "chkPt1.hdf5")
    cap = cv2.VideoCapture('startV.mp4')
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (1366, 800))
            cv2.imshow('Facial Expression Recognition',frame) #Window name, image to be displayed
            cv2.waitKey(1)
        else:
            break
    cap.release()
    start_app(model) # Model is the CNN
