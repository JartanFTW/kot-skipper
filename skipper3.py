import pyautogui
import os
import time
import asyncio
import cv2 as cv
import numpy as np

### config

CONFIDENCE = 0.80
GRAYSCALE = True
DELAY = 1
TASKS = 5

###


PATH = os.getcwd()
GEMS = [os.path.join(PATH, "imgs", x) for x in os.listdir(os.path.join(PATH, "gems"))]


async def main():

    sem = asyncio.Semaphore(TASKS)

    while True:

        sc = pyautogui.screenshot()
        sc = cv.cvtColor(np.array(sc), cv.COLOR_RGB2BGR)

        for gem in GEMS:
            print(gem)
            img_object = cv.imread(gem, cv.IMREAD_GRAYSCALE)
            img_scene = sc

            minHessian = 400
            detector = cv.xfeatures2d_SURF.create(hessianThreshold=minHessian)
            keypoints_obj, descriptors_obj = detector.detectAndCompute(img_object, None)
            keypoints_scene, descriptors_scene = detector.detectAndCompute(
                img_scene, None
            )
            # -- Step 2: Matching descriptor vectors with a FLANN based matcher
            # Since SURF is a floating-point descriptor NORM_L2 is used
            matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
            knn_matches = matcher.knnMatch(descriptors_obj, descriptors_scene, 2)
            # -- Filter matches using the Lowe's ratio test
            ratio_thresh = 0.75
            good_matches = []
            for m, n in knn_matches:
                if m.distance < ratio_thresh * n.distance:
                    good_matches.append(m)
            # -- Draw matches
            img_matches = np.empty(
                (
                    max(img_object.shape[0], img_scene.shape[0]),
                    img_object.shape[1] + img_scene.shape[1],
                    3,
                ),
                dtype=np.uint8,
            )
            cv.drawMatches(
                img_object,
                keypoints_obj,
                img_scene,
                keypoints_scene,
                good_matches,
                img_matches,
                flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
            )
            # -- Localize the object
            obj = np.empty((len(good_matches), 2), dtype=np.float32)
            scene = np.empty((len(good_matches), 2), dtype=np.float32)
            for i in range(len(good_matches)):
                # -- Get the keypoints from the good matches
                obj[i, 0] = keypoints_obj[good_matches[i].queryIdx].pt[0]
                obj[i, 1] = keypoints_obj[good_matches[i].queryIdx].pt[1]
                scene[i, 0] = keypoints_scene[good_matches[i].trainIdx].pt[0]
                scene[i, 1] = keypoints_scene[good_matches[i].trainIdx].pt[1]
            H, _ = cv.findHomography(obj, scene, cv.RANSAC)
            # -- Get the corners from the image_1 ( the object to be "detected" )
            obj_corners = np.empty((4, 1, 2), dtype=np.float32)
            obj_corners[0, 0, 0] = 0
            obj_corners[0, 0, 1] = 0
            obj_corners[1, 0, 0] = img_object.shape[1]
            obj_corners[1, 0, 1] = 0
            obj_corners[2, 0, 0] = img_object.shape[1]
            obj_corners[2, 0, 1] = img_object.shape[0]
            obj_corners[3, 0, 0] = 0
            obj_corners[3, 0, 1] = img_object.shape[0]
            scene_corners = cv.perspectiveTransform(obj_corners, H)
            # -- Draw lines between the corners (the mapped object in the scene - image_2 )
            cv.line(
                img_matches,
                (
                    int(scene_corners[0, 0, 0] + img_object.shape[1]),
                    int(scene_corners[0, 0, 1]),
                ),
                (
                    int(scene_corners[1, 0, 0] + img_object.shape[1]),
                    int(scene_corners[1, 0, 1]),
                ),
                (0, 255, 0),
                4,
            )
            cv.line(
                img_matches,
                (
                    int(scene_corners[1, 0, 0] + img_object.shape[1]),
                    int(scene_corners[1, 0, 1]),
                ),
                (
                    int(scene_corners[2, 0, 0] + img_object.shape[1]),
                    int(scene_corners[2, 0, 1]),
                ),
                (0, 255, 0),
                4,
            )
            cv.line(
                img_matches,
                (
                    int(scene_corners[2, 0, 0] + img_object.shape[1]),
                    int(scene_corners[2, 0, 1]),
                ),
                (
                    int(scene_corners[3, 0, 0] + img_object.shape[1]),
                    int(scene_corners[3, 0, 1]),
                ),
                (0, 255, 0),
                4,
            )
            cv.line(
                img_matches,
                (
                    int(scene_corners[3, 0, 0] + img_object.shape[1]),
                    int(scene_corners[3, 0, 1]),
                ),
                (
                    int(scene_corners[0, 0, 0] + img_object.shape[1]),
                    int(scene_corners[0, 0, 1]),
                ),
                (0, 255, 0),
                4,
            )
            # -- Show detected matches
            cv.imshow("Good Matches & Object detection", img_matches)
            cv.waitKey()

            # template = cv.imread(im, 0)

            # res = cv.matchTemplate(sc, template, cv.TMCCOEFF)

        # for i in range(len(res)):
        # if res[i]:
        # print(f"Found {os.path.basename(GEMS[i])}")
        # print(res)

        print("sleeping")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
