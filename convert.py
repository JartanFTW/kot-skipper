import os
from PIL import Image
import numpy as np
import cv2

PATH = os.getcwd()

gems = [x for x in os.listdir(os.path.join(PATH, "imgs EXAMPLE"))]

for gem in gems:
    img = cv2.imread(os.path.join(PATH, "imgs EXAMPLE", gem))
    
    cv2.imwrite(os.path.join(PATH, "toconv", f"{gem[:-4]}.png"), img)