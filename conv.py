import os
from PIL import Image
import numpy as np
import cv2

PATH = os.getcwd()

gems = [x for x in os.listdir(os.path.join(PATH, "imgs EXAMPLE"))]


for x in gems:
    # with Image.open(x) as im:
        # im = im.convert("RGBA")
        
        # im.save(x[:-4], format="PNG")
    
    img = cv2.imread(os.path.join(PATH, "imgs EXAMPLE", x))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    mask = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)[1]
    
    mask = 255 - mask
    
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # anti-alias the mask -- blur then stretch
    # blur alpha channel
    mask = cv2.GaussianBlur(mask, (0,0), sigmaX=2, sigmaY=2, borderType = cv2.BORDER_DEFAULT)

    # linear stretch so that 127.5 goes to 0, but 255 stays 255
    mask = (2*(mask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)

    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask

    # save resulting masked image
    print(os.path.join(PATH, "toconv", x[:-4], ".png"))
    cv2.imwrite(os.path.join(PATH, "toconv", f"{x[:-4]}.png"), result)
    
    # display result, though it won't show transparency
    # cv2.imshow("INPUT", img)
    # cv2.imshow("GRAY", gray)
    # cv2.imshow("MASK", mask)
    # cv2.imshow("RESULT", result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    # os.remove(os.path.join(PATH, "gems", x))