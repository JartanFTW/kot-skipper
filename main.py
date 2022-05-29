# Standard
import asyncio
import argparse
from ctypes import windll
from numpy import array
import os
import pyautogui
import pyscreeze
import sys
from win32api import PostMessage, MAKELONG
from win32ui import CreateDCFromHandle, CreateBitmap
from win32gui import (
    FindWindow,
    FindWindowEx,
    GetWindowRect,
    GetWindowDC,
    DeleteObject,
    ReleaseDC,
)
from win32con import WM_LBUTTONDOWN, MK_LBUTTON, WM_LBUTTONUP

# Third Party
import easyocr
from PIL import Image, ImageGrab, ImageDraw

# Local


global ARGS, PATH, debug_window_counter, debug_chest_counter, debug_slot_counter, debug_name_counter


def parse_arguments(argv=None):
    """
    Parses command line arguments and returns them
    """

    parser = argparse.ArgumentParser(
        description="A command line tool for the mobile game King of Thieves"
    )

    parser.add_argument(
        "emulator",
        help="which emulator is being used",
        type=str,
        choices=["bluestacks"],
    )

    parser.add_argument(
        "-gd",
        "--gold",
        help="pause when this amount of gold or more is found",
        type=int,
    )
    gem_choices = [
        "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", 
        "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", 
        "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", 
        "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", 
        "y1", "y2", "y3", "y4", "y5", "y6", "y7", "y8"
    ]  # fmt: skip
    parser.add_argument(
        "-gm",
        "--gems",
        help="which gems to target  format: r8 r7 b7 b8 y5",
        type=str,
        nargs="*",
        choices=gem_choices,
    )

    parser.add_argument(
        "-r",
        "--retries",
        help="how many retries to perform on failed identification tasks",
        type=int,
        default=2,
    )

    parser.add_argument(
        "-d",
        "--delay",
        help="how many seconds to wait between retries and after skipping",
        type=float,
        default=5,
    )

    parser.add_argument(
        "--debug",
        help="what type of debug images to save",
        type=str,
        nargs="*",
        choices=["window", "chest", "slot", "name"],
    )

    args = parser.parse_args(argv)

    # guaranteeing positive int
    args.retries = abs(args.retries)
    # guaranteeing emulator lower-case
    args.emulator = args.emulator.lower()

    return args


def _screenshot_window(window) -> Image:
    # https://stackoverflow.com/a/24352388

    dimensions = GetWindowRect(window)

    hwndDC = GetWindowDC(window)
    mfcDC = CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(
        mfcDC, dimensions[2] - dimensions[0], dimensions[3] - dimensions[1]
    )

    saveDC.SelectObject(saveBitMap)

    windll.user32.PrintWindow(window, saveDC.GetSafeHdc(), 0)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    image = Image.frombuffer(
        "RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1
    )

    DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    ReleaseDC(window, hwndDC)

    return image


async def screenshot_window(window) -> Image:
    res = await asyncio.to_thread(_screenshot_window, window)

    if ARGS.debug and "window" in ARGS.debug:
        global debug_window_counter
        output_path = os.path.join(PATH, "output", f"window_{debug_window_counter}.png")
        debug_window_counter += 1
        asyncio.create_task(asyncio.to_thread(res.save, output_path))

    return res


def get_best_text_result(results, type=None):
    confidence = 0
    best = None

    for res in results:
        if res[2] > confidence:
            if type:
                try:
                    type(res[1])
                except Exception:
                    continue
            confidence = res[2]
            best = res[1]

    if best:
        return (best, res)
    return None


async def find_dungeon_owner(game, ocr: easyocr.Reader) -> str | None:
    # this function is not used (and doesn't work very well)
    sc = await screenshot_window(game)
    dimensions = sc.size
    dimensions = (
        0,
        dimensions[1] - int(dimensions[1] * 0.125),
        dimensions[0],
        dimensions[1],
    )
    crop = sc.crop(dimensions)

    if ARGS.debug and "name" in ARGS.debug:
        global debug_name_counter
        output_path = os.path.join(PATH, "output", f"name_{debug_name_counter}.png")
        debug_name_counter += 1
        asyncio.create_task(asyncio.to_thread(crop.save, output_path))

    image_array = array(crop)

    results = await asyncio.to_thread(ocr.readtext, image_array)
    result = get_best_text_result(results)

    if result:
        return result[0]
    return None


async def locate(img, bg, gs=True, conf=0.90):
    res = await asyncio.to_thread(
        pyscreeze.locate, img, bg, grayscale=gs, confidence=conf
    )
    return res


async def find_dungeon_gold(
    game, ocr: easyocr.Reader, retries=None, delay=None
) -> int | None:
    if not retries:
        retries = ARGS.retries
    if not delay:
        delay = ARGS.delay
    retry = -1  # need to guarantee 1 retry
    chest_image = os.path.join(PATH, "assets", "chest.png")

    while retry < retries:
        if retry != -1:
            await asyncio.sleep(delay)
        retry += 1

        sc = await screenshot_window(game)

        chest_location = await locate(
            chest_image, sc, gs=False, conf=0.50
        )  # TODO confidence to command line parameter if needed
        if not chest_location:
            print("Failed to identify chest location")
            continue
        chest_location = (
            *chest_location[:2],
            chest_location[0] + chest_location[2],
            chest_location[1] + chest_location[3],
        )

        chest = sc.crop(chest_location)

        if ARGS.debug and "chest" in ARGS.debug:
            global debug_chest_counter
            output_path = os.path.join(
                PATH, "output", f"chest_{debug_chest_counter}.png"
            )
            debug_chest_counter += 1
            asyncio.create_task(asyncio.to_thread(chest.save, output_path))

        chest_array = array(chest)

        results = await asyncio.to_thread(
            ocr.readtext, chest_array, allowlist="0123456789", low_text=0.5
        )
        # TODO low_text to command line parameter if needed
        result = get_best_text_result(results, type=int)

        if not result:
            print("Failed to identify chest text")
            continue

        return int(result[0])


async def find_dungeon_gems(game):
    # WIP
    return None


async def skip_dungeon(game) -> None:
    skip_image = os.path.join(PATH, "assets", "skip.png")

    sc = await screenshot_window(game)

    skip_location = await locate(skip_image, sc)

    if not skip_location:
        print("Failed to locate skip button")
        return

    click_position = (
        skip_location[0] + int(skip_location[2] / 2),
        skip_location[1] + int(skip_location[3] / 2),
    )

    click_position = MAKELONG(*click_position)

    if ARGS.emulator == "bluestacks":
        game_window = FindWindowEx(game, None, None, None)

    PostMessage(game_window, WM_LBUTTONDOWN, MK_LBUTTON, click_position)
    PostMessage(game_window, WM_LBUTTONUP, None, click_position)

    await asyncio.sleep(ARGS.delay)

    return


async def main():
    global ARGS, PATH

    print("Press CTRL + C on this console to exit at any time")

    # setup

    if getattr(sys, "frozen", False):  # handles compiled to exe
        PATH = os.path.dirname(sys.executable)
    else:
        PATH = os.path.dirname(os.path.abspath(__file__))

    ARGS = parse_arguments(sys.argv[1:])
    retries = -1
    last_gold = 0

    if ARGS.emulator == "bluestacks":
        game = FindWindow(None, "BlueStacks")
    assert game

    if ARGS.debug:
        if "window" in ARGS.debug:
            global debug_window_counter
            debug_window_counter = 1
        if "chest" in ARGS.debug:
            global debug_chest_counter
            debug_chest_counter = 1
        if "slot" in ARGS.debug:
            global debug_slot_counter
            debug_slot_counter = 1
        if "name" in ARGS.debug:
            global debug_name_counter
            debug_name_counter = 1

    ocr = easyocr.Reader(["en"])

    # start

    while True:
        gold, gems = await asyncio.gather(
            find_dungeon_gold(game, ocr),
            find_dungeon_gems(game),
        )

        if gold and ARGS.gold and gold >= ARGS.gold:
            print(f"Dungeon gold {gold} fulfills stop requirement of {ARGS.gold} gold")
            input(f"Press enter to continue")
            continue
        elif gems and ARGS.gems and any(gems) in ARGS.gems:
            print("Dungeon gems ", " ".join(gems), "fulfills gem stop requirement")
            input(f"Press enter to continue")
            continue

        # validates new dungeon, skipping or waiting if same as last
        if gold == last_gold:
            print("Dungeon same as last dungeon")

            if retries >= ARGS.retries:
                retries = -1
                await skip_dungeon(game)
                continue
            await asyncio.sleep(ARGS.delay)
            retries += 1
            continue

        retries = -1
        last_gold = gold

        await skip_dungeon(game)


if __name__ == "__main__":
    asyncio.run(main())
