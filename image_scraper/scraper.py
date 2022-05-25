"""
This program takes screenshots constantly, checking them for totem chests. If a totem chest is detected, it crops the screenshot to the gem slots.
Config is directly below imports.
"""

import pyautogui
import os
import asyncio
from keyboard import send
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageShow
from math import floor

### config

CHEST_IDENTIFICATION_GRAYSCALE = True
CHEST_IDENTIFICATION_CONFIDENCE = 0.50

SKIP = True
SKIP_DELAY = 0.5

SAVE_SCREENSHOTS = False
SAVE_TOTEM_SUCCESS = False
SAVE_TOTEM_FAILURE = False
SAVE_SLOT_IMAGES = True

### end config

PATH = os.getcwd()
OUTPUT = os.path.join(PATH, "output")
ASSETS = os.path.join(PATH, "assets")

###


async def locate(img, bg, gs=True, conf=0.90):
    res = await asyncio.to_thread(
        pyautogui.locate, img, bg, grayscale=gs, confidence=conf
    )
    return res


async def locate_gem_slots(
    screen, gs=CHEST_IDENTIFICATION_GRAYSCALE, conf=CHEST_IDENTIFICATION_CONFIDENCE
):

    # attempt to get slot locations using chest
    chest = os.path.join(ASSETS, "chest.png")
    totem = await locate(chest, screen, gs=gs, conf=conf)

    if totem:
        slots = [totem[0], totem[1], totem[2], totem[3]]

        # moving top left corner up by 75% of chest height
        slots[1] -= round(totem[3] * 0.75)
        # moving top left corner left by 10% of chest width
        slots[0] -= round(totem[2] * 0.1)

        # setting height to 60% of chest height
        slots[3] = round(totem[3] * 0.60)
        # setting width to 125% of chest width
        slots[2] = round(totem[2] * 1.25)

        return slots

    return False


async def pause_or_continue():
    if SKIP:
        send("space")
        await asyncio.sleep(SKIP_DELAY)
    else:
        input("Press Enter to re-scan")
        print("---")
        print("Beginning in 5 seconds")
        await asyncio.sleep(5)


async def main():

    ## setup stuff

    if SAVE_SCREENSHOTS:
        screenshot_count = (
            len([x for x in os.listdir(OUTPUT) if x.startswith("screenshot_")]) + 1
        )
    if SAVE_TOTEM_FAILURE:
        slots_search_failure = (
            len([x for x in os.listdir(OUTPUT) if x.startswith("slots_failed_")]) + 1
        )
    if SAVE_TOTEM_SUCCESS:
        slots_search_success = (
            len([x for x in os.listdir(OUTPUT) if x.startswith("slots_success_")]) + 1
        )
    if SAVE_SLOT_IMAGES:
        slot_count = len([x for x in os.listdir(OUTPUT) if x.startswith("slot")]) + 1

    # start

    print("Beginning in 5 seconds")
    await asyncio.sleep(5)

    while True:

        screen = pyautogui.screenshot()

        if SAVE_SCREENSHOTS:
            screen.save(os.path.join(OUTPUT, f"screenshot_{screenshot_count}.png"))
            screenshot_count += 1

        # Identify slots

        slots = await locate_gem_slots(screen)

        if not slots:
            print("Failed to locate slots")

            if SAVE_TOTEM_FAILURE:
                screen.save(
                    os.path.join(OUTPUT, f"slots_failed_{slots_search_failure}.png")
                )
                slots_search_failure += 1

            await pause_or_continue()
            continue

        # crop to gem slots

        slots = screen.crop(
            (slots[0], slots[1], slots[0] + slots[2], slots[1] + slots[3])
        )

        if SAVE_TOTEM_SUCCESS:
            slots.save(
                os.path.join(OUTPUT, f"slots_success_{slots_search_success}.png")
            )
            slots_search_success += 1

        # Split slots into three sections
        slot_dimensions = []
        x, y = slots.size
        x3 = floor(x / 3)
        slot_dimensions = [(0, 0, x3, y), (x3, 0, x3 * 2, y), (x3 * 2, 0, x, y)]

        for dimension in slot_dimensions:

            slot = slots.crop(dimension)
            if SAVE_SLOT_IMAGES:
                slot.save(os.path.join(OUTPUT, f"slot_{slot_count}.png"))
                slot_count += 1

        await pause_or_continue()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
