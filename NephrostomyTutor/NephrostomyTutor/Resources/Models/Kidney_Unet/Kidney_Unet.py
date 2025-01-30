import numpy
import torch
import argparse
import traceback
import sys
import json
import os
import numpy as np
import cv2
from pathlib import Path

class Kidney_Unet:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.extra_files = {"config.json": ""}

    def loadModel(self,model_path):
        self.model = torch.jit.load(os.path.join(model_path,"model_traced_best.pt"), _extra_files=self.extra_files).to(self.device)
        self.config = json.loads(self.extra_files["config.json"])
        self.input_size = self.config["shape"][-1]

    def predict(self,image):
        orig_img_size = image.shape
        image = self.preprocess_input(image, self.input_size).to(self.device)

        # Run inference
        with torch.inference_mode():
            prediction = self.model(image)

        if isinstance(prediction, list):
            prediction = prediction[0]

        prediction = torch.nn.functional.softmax(prediction, dim=1)
        prediction = self.postprocess_prediction(prediction, orig_img_size)
        return prediction

    def preprocess_input(self,image, input_size):
        image = numpy.expand_dims(cv2.resize(image, (input_size, input_size)),axis=-1)  # default is bilinear
        image = numpy.concatenate([image,image,image],axis=-1)
        image = numpy.transpose(image,(2,0,1))
        image = torch.from_numpy(image).unsqueeze(0).float()
        return image

    def postprocess_prediction(self,prediction, original_size):
        prediction = prediction.squeeze().detach().cpu().numpy() * 255
        prediction = numpy.transpose(prediction,(1,2,0))
        prediction = numpy.argmax(prediction, axis=-1).astype(np.uint8)
        prediction = cv2.resize(prediction, (original_size[1], original_size[0]))
        prediction = prediction.astype(np.uint8)
        print(prediction.shape)
        return prediction
