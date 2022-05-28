"""
This program takes screenshots constantly, checking them for totem chests. If a totem chest is detected, it crops the screenshot to the gem slots.
Config is directly below imports.
"""

import pyautogui
import os
import asyncio
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageShow, ImageGrab
import pygetwindow
from win32gui import FindWindow, FindWindowEx, GetWindowRect
from win32api import PostMessage, MAKELONG
from win32con import WM_LBUTTONDOWN, MK_LBUTTON, WM_LBUTTONUP
from math import floor
import easyocr
from numpy import array

### config

GAME_WINDOW_TITLE = "BlueStacks"
BLUESTACKS = True


SKIP = True
# If the program skips a target and then stops, increase this delay
SKIP_DELAY = 0.6
# How many pixels north-west from bottom right of game window to click for skip
SKIP_BUTTON_OFFSET = 50


# set to False to disable
# REQUIRES INSTALLATION OF https://github.com/madmaze/pytesseract
GOLD_TARGET = 20000

CHEST_IDENTIFICATION_GRAYSCALE = False
CHEST_IDENTIFICATION_CONFIDENCE = 0.50

GOLD_TEXT_IDENTIFICATION_MIN_THRESHOLD = 0.5
TEXT_CONFIDENCE_THRESHOLD = 0.65

### end config

PATH = os.getcwd()
ASSETS = os.path.join(PATH, "assets")

###


async def locate(img, bg, gs=True, conf=0.90):
    res = await asyncio.to_thread(
        pyautogui.locate, img, bg, grayscale=gs, confidence=conf
    )
    return res


async def locate_chest(
    screen, gs=CHEST_IDENTIFICATION_GRAYSCALE, conf=CHEST_IDENTIFICATION_CONFIDENCE
):
    chest = os.path.join(ASSETS, "chest.png")
    totem = await locate(chest, screen, gs=gs, conf=conf)
    if totem:
        return [totem[0], totem[1], totem[2], totem[3]]
    return False


async def get_chest_gold(chest, ocr: easyocr.Reader):
    chest_array = array(chest.resize((100, 100)))
    results = ocr.readtext(
        chest_array,
        allowlist="0123456789",
        low_text=GOLD_TEXT_IDENTIFICATION_MIN_THRESHOLD,
    )
    best_conf = 0
    best = None
    for res in results:
        if res[2] > best_conf:
            try:
                int(res[1])
            except (TypeError, ValueError):
                continue

            best_conf = res[2]
            best = res[1]

    if best_conf < TEXT_CONFIDENCE_THRESHOLD:
        return None
    return int(best)


async def locate_gem_slots(
    screen, gs=CHEST_IDENTIFICATION_GRAYSCALE, conf=CHEST_IDENTIFICATION_CONFIDENCE
):

    # attempt to get slot locations using chest
    slots = await locate_chest(screen)

    if slots:

        # moving top left corner up by 75% of chest height
        slots[1] -= round(slots[3] * 0.75)
        # moving top left corner left by 10% of chest width
        slots[0] -= round(slots[2] * 0.1)

        # setting height to 60% of chest height
        slots[3] = round(slots[3] * 0.60)
        # setting width to 125% of chest width
        slots[2] = round(slots[2] * 1.25)

        return slots

    return False


async def pause_or_continue(found=False, game_window=None):

    if not found and SKIP:

        # get position of window and find skip button position relative to it
        position = GetWindowRect(game_window)
        position = MAKELONG(
            position[2] - position[0] - SKIP_BUTTON_OFFSET,
            position[3] - position[1] - SKIP_BUTTON_OFFSET,
        )

        if BLUESTACKS:
            game_window = FindWindowEx(game_window, None, None, None)

        # click skip
        PostMessage(game_window, WM_LBUTTONDOWN, MK_LBUTTON, position)
        PostMessage(game_window, WM_LBUTTONUP, None, position)

        await asyncio.sleep(SKIP_DELAY)
    else:
        input("Press Enter to continue")
        print("---")
        print("Beginning in 5 seconds")
        await asyncio.sleep(5)


async def main():

    # setup

    if GOLD_TARGET:
        ocr = easyocr.Reader(["en"])

    retry = False

    # start

    print("Beginning in 5 seconds")
    await asyncio.sleep(5)

    while True:

        game_window = FindWindow(None, GAME_WINDOW_TITLE)
        game_window_rectangle = GetWindowRect(game_window)

        # screenshot window using PIL
        screen = ImageGrab.grab(bbox=game_window_rectangle, all_screens=True)

        # Checking for gold

        if GOLD_TARGET:
            chest = await locate_chest(screen)

            if chest:
                chest_crop = screen.crop(
                    (chest[0], chest[1], chest[0] + chest[2], chest[1] + chest[3])
                )

                # + 25 to add buffer to help prevent OCR mistaking for chest edge for #1

                gold = await get_chest_gold(chest_crop, ocr)
                if gold:
                    print(f"Detected {gold} gold")
                    if gold > GOLD_TARGET:
                        print(f"Found target with {gold} gold")
                        await pause_or_continue(found=True, game_window=game_window)
                        continue
                else:
                    if not retry:
                        print("Failed to detect gold count - retrying in 5 seconds")
                        await asyncio.sleep(5)
                        retry = True
                        continue
                    print("Failed to detect gold count - skipping")
                    retry = False
                    await pause_or_continue(game_window=game_window)
                    continue

        # Identify slots

        slots = await locate_gem_slots(screen)

        if not slots:
            if not retry:
                print("Failed to locate slots - retrying in 5 seconds")
                await asyncio.sleep(5)
                retry = True
                continue
            print("Failed to locate slots - skipping")
            retry = False
            await pause_or_continue(game_window=game_window)
            continue

        # crop to gem slots

        slots = screen.crop(
            (slots[0], slots[1], slots[0] + slots[2], slots[1] + slots[3])
        )

        # Split slots into three sections
        slot_dimensions = []
        x, y = slots.size
        x3 = floor(x / 3)
        slot_dimensions = [(0, 0, x3, y), (x3, 0, x3 * 2, y), (x3 * 2, 0, x, y)]

        for dimension in slot_dimensions:

            slot = slots.crop(dimension)

        await pause_or_continue(game_window=game_window)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
