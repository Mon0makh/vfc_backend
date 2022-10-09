# DataFlair background removal

# import necessary packages
import cv2
import numpy as np

def remove_background(path: str):
    # 720 - 1280
    img = cv2.imread(path)


    # 719 - 1080
    # mask = cv2.imread("./images/mask2.png")
    # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    #
    # transparent = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)
    # transparent[:, :, 0:3] = img
    # transparent[:, :, 3] = mask

    print("Shape of the image", img.shape)

    # [rows, columns]
    crop = img[200:1280, 0:720]

    cv2.imwrite(path, crop)

