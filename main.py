# Standard
import asyncio
import argparse
from ctypes import windll
from math import floor, ceil
from numpy import array
import os
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
from PIL import Image
from tensorflow import keras

# Local


global ARGS, PATH, debug_window_counter, debug_chest_counter, debug_slot_counter, debug_name_counter, debug_slots_counter, debug_gems_counter, debug_tasks


class GemIdentifier:
    def __init__(self):
        self.model = keras.models.load_model(os.path.join(PATH, "identify_gem"))
        self.gems = [
            "0",
            'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 
            'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 
            'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 
            'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 
            'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8']  # fmt: skip

    def identify_gem(self, image: Image):
        resized_image = image.resize((50, 50), resample=Image.Resampling.NEAREST)
        resized_array = array(resized_image)
        input_array = array([resized_array])
        prediction = self.model.predict(input_array, verbose=0).tolist()

        result = (self.gems[prediction.index(max(prediction))], max(prediction))
        return result

    def identify_gems(self, images: list):
        image_arrays = []
        for image in images:
            resized_image = image.resize((50, 50), resample=Image.Resampling.NEAREST)
            resized_array = array(resized_image)
            image_arrays.append(resized_array)
        input_array = array(image_arrays)
        predictions = [x.tolist() for x in self.model.predict(input_array, verbose=0)]

        results = [(self.gems[x.index(max(x))], max(x)) for x in predictions]
        return results


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
        "1", "2", "3", "4", "5", "6", "7", "8", 
        "r", "b", "g", "p", "y",
        "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", 
        "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", 
        "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", 
        "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", 
        "y1", "y2", "y3", "y4", "y5", "y6", "y7", "y8"
    ]  # fmt: skip
    parser.add_argument(
        "-gm",
        "--gems",
        help="pause when any of these gems are found",
        type=str,
        nargs="*",
        choices=gem_choices,
    )

    parser.add_argument(
        "-r",
        "--retries",
        help="how many retries to perform on failed identification tasks",
        type=int,
        default=6,
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
        choices=[
            "window",
            "chest",
            "slots",
            "slot",
            "gems",
            "tgems",
            "name",
            "screenshotmode",
        ],
    )

    args = parser.parse_args(argv)

    # guaranteeing positive int
    args.retries = abs(args.retries)
    # guaranteeing emulator lower-case
    args.emulator = args.emulator.lower()

    # parsing gem args
    if args.gems:
        # collects lone integers (tiers)
        tiers = [x for x in args.gems if x.isdigit()]
        # collects lone strings (colors)
        colors = [x for x in args.gems if not any(char.isdigit() for char in x)]
        # guarantees a char and a digit for all remaining
        args.gems = [
            x
            for x in args.gems
            if not x.isdigit() and any(char.isdigit() for char in x)
        ]
        # if a tier is provided, add all colors of that tier
        for tier in tiers:
            for color in ["r", "b", "g", "p", "y"]:
                if f"{color}{tier}" not in args.gems:
                    args.gems.append(f"{color}{tier}")
        # if a color is provided, add all tiers of that color
        for color in colors:
            for tier in range(1, 9):
                if f"{color}{tier}" not in args.gems:
                    args.gems.append(f"{color}{tier}")

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
        global debug_window_counter, debug_tasks
        output_path = os.path.join(PATH, "output", f"window_{debug_window_counter}.png")
        debug_window_counter += 1
        debug_tasks.append(
            asyncio.create_task(asyncio.to_thread(res.save, output_path))
        )

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
        global debug_name_counter, debug_tasks
        output_path = os.path.join(PATH, "output", f"name_{debug_name_counter}.png")
        debug_name_counter += 1
        debug_tasks.append(
            asyncio.create_task(asyncio.to_thread(crop.save, output_path))
        )

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
    game, ocr: easyocr.Reader | None, retries=None, delay=None
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
            print(f"Failed to identify chest location - {retry + 1}")
            continue
        chest_location = (
            *chest_location[:2],
            chest_location[0] + chest_location[2],
            chest_location[1] + chest_location[3],
        )

        chest = sc.crop(chest_location)

        if ARGS.debug and "chest" in ARGS.debug:
            global debug_chest_counter, debug_tasks
            output_path = os.path.join(
                PATH, "output", f"chest_{debug_chest_counter}.png"
            )
            debug_chest_counter += 1
            debug_tasks.append(
                asyncio.create_task(asyncio.to_thread(chest.save, output_path))
            )
        if ARGS.debug and "screenshotmode" in ARGS.debug:
            return

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
    print(f"Failed to identify chest location {retries + 2} times")


async def find_gem_slots(game, retries=None, delay=None):
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
            print(f"Failed to identify chest location - {retry + 1}")
            continue

        slots = [
            chest_location[0],
            chest_location[1],
            chest_location[2],
            chest_location[3],
        ]

        # move NW corner left by 10% of chest width
        slots[0] = floor(slots[0] - slots[2] * 0.1)
        # move NW corner up by 75% of chest height
        slots[1] = floor(slots[1] - slots[3] * 0.75)
        # expand width by 20%
        slots[2] = ceil(slots[2] * 1.2)
        # reduce height by 40%
        slots[3] = ceil(slots[3] * 0.60)

        slots = sc.crop((slots[0], slots[1], slots[0] + slots[2], slots[1] + slots[3]))

        if ARGS.debug and "slots" in ARGS.debug:
            global debug_slots_counter, debug_tasks
            output_path = os.path.join(
                PATH, "output", f"slots_{debug_slots_counter}.png"
            )
            debug_slots_counter += 1
            debug_tasks.append(
                asyncio.create_task(asyncio.to_thread(slots.save, output_path))
            )

        return slots

    print("Failed to identify gem slots")
    return None


def find_individual_gem_slots(slots):

    x, y = slots.size
    x3, rem = divmod(x, 3)
    # division remainder is included to reduce images getting cut off
    slot_dimensions = [
        (0, 0, x3 + rem, y),
        (x3 - rem, 0, x3 * 2 + rem, y),
        (x3 * 2 - rem, 0, x, y),
    ]

    individual_slots = []
    for dimension in slot_dimensions:

        slot = slots.crop(dimension)
        individual_slots.append(slot)

        if ARGS.debug and "slot" in ARGS.debug:
            global debug_slot_counter, debug_tasks
            output_path = os.path.join(PATH, "output", f"slot_{debug_slot_counter}.png")
            debug_slot_counter += 1
            debug_tasks.append(
                asyncio.create_task(asyncio.to_thread(slot.save, output_path))
            )

    return individual_slots


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


async def find_dungeon_gems(game, identifier: GemIdentifier):

    slots = await find_gem_slots(game)
    if not slots:
        return None
    slots = find_individual_gem_slots(slots)

    gems = identifier.identify_gems(slots)

    i = -1
    for gem in gems:
        i += 1
        if ARGS.debug:
            global debug_gems_counter, debug_tasks
            if "gems" in ARGS.debug:
                create_dir(os.path.join(PATH, "output", gem[0]))
                output_path = os.path.join(
                    PATH, "output", gem[0], f"{gem[0]}_{debug_gems_counter}.png"
                )
                debug_gems_counter += 1
                debug_tasks.append(
                    asyncio.create_task(asyncio.to_thread(slots[i].save, output_path))
                )
            elif "tgems" in ARGS.debug and gem[0] in ARGS.gems:
                create_dir(os.path.join(PATH, "output", gem[0]))
                output_path = os.path.join(
                    PATH, "output", gem[0], f"{gem[0]}_{debug_gems_counter}.png"
                )
                debug_gems_counter += 1
                debug_tasks.append(
                    asyncio.create_task(asyncio.to_thread(slots[i].save, output_path))
                )
    return gems


async def skip_dungeon(game) -> None:
    skip_image = os.path.join(PATH, "assets", "skip.png")

    sc = await screenshot_window(game)

    skip_location = await locate(skip_image, sc, conf=0.7)

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


async def ainput(text=None):
    res = await asyncio.to_thread(input, text)
    return res


async def main():
    global ARGS, PATH

    print("Press CTRL + C on this console to exit at any time")

    # setup

    if getattr(sys, "frozen", False):  # handles compiled to exe
        PATH = os.path.dirname(sys.executable)
    else:
        PATH = os.path.dirname(os.path.abspath(__file__))

    ARGS = parse_arguments(sys.argv[1:])
    retries = 0
    last_gold = 0

    if ARGS.emulator == "bluestacks":
        game = FindWindow(None, "BlueStacks")
    assert game

    if ARGS.debug:
        global debug_tasks
        debug_tasks = []
        if "window" in ARGS.debug:
            global debug_window_counter
            debug_window_counter = 1
        if "chest" in ARGS.debug:
            global debug_chest_counter
            debug_chest_counter = 1
        if "slots" in ARGS.debug:
            global debug_slots_counter
            debug_slots_counter = 1
        if "slot" in ARGS.debug:
            global debug_slot_counter
            debug_slot_counter = 1
        if "name" in ARGS.debug:
            global debug_name_counter
            debug_name_counter = 1
        if "gems" in ARGS.debug or "tgems" in ARGS.debug:
            global debug_gems_counter
            debug_gems_counter = 1

    gem_identifier = GemIdentifier()

    # debug screenshot mode
    if ARGS.debug and "screenshotmode" in ARGS.debug:
        try:
            while True:
                await ainput("Press enter when a totem is visible")
                await asyncio.gather(
                    find_dungeon_gold(game, None),
                    find_dungeon_gems(game, gem_identifier),
                )
                await asyncio.wait(debug_tasks)
        except KeyboardInterrupt:
            # prevents keyboardinterrupt causing normal program function to begin
            return

    # placed after debug screenshot mode to prevent unnecessary launching
    ocr = easyocr.Reader(["en"])

    # start

    while True:
        gold, gems = await asyncio.gather(
            find_dungeon_gold(game, ocr),
            find_dungeon_gems(game, gem_identifier),
        )

        # validates new dungeon, skipping or waiting if same as last
        if gold == last_gold:
            if retries >= ARGS.retries:
                print("Dungeon same as last dungeon - skipping")
                retries = 0
                await skip_dungeon(game)
                continue
            print("Dungeon same as last dungeon - waiting")
            await asyncio.sleep(ARGS.delay)
            retries += 1
            continue

        retries = 0
        last_gold = gold

        if gold and ARGS.gold and gold >= ARGS.gold:
            print(f"Dungeon gold {gold} fulfills stop requirement of {ARGS.gold} gold")
            await ainput(f"Press enter to continue")
            continue

        if gems and ARGS.gems and any(x in ARGS.gems for x in [x[0] for x in gems]):
            print(
                "Dungeon gems",
                " ".join([x[0] for x in gems]),
                "fulfills gem stop requirement",
            )
            await ainput(f"Press enter to continue")
            continue

        await skip_dungeon(game)


if __name__ == "__main__":
    asyncio.run(main())
