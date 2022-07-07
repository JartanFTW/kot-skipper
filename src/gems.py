from math import floor, ceil
from numpy import array
import os

from PIL import Image
from pyscreeze import locate
from tensorflow import keras

from .errors import ChestNotFoundException
from .utils import write_image, create_dir


class GemIdentifier:
    def __init__(self, path: str, tgems: list = None, debug: list = None):
        self.path = path
        self.tgems = tgems
        self.debug = debug

        self.model = keras.models.load_model(os.path.join(path, "identify_gem.h5"))
        self.categories = [
            "0",
            "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", 
            "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", 
            "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", 
            "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", 
            "y1", "y2", "y3", "y4", "y5", "y6", "y7", "y8"]  # fmt: skip

        self.chest = Image.open(os.path.join(path, "assets", "chest.png"))

    def _find_slots(self, screenshot: Image):
        chest = locate(self.chest, screenshot, grayscale=False, confidence=0.5)

        if not chest:
            raise ChestNotFoundException("identifying slots")

        slots = [
            chest[0],
            chest[1],
            chest[2],
            chest[3],
        ]

        # move NW corner left by 10% of chest width
        slots[0] = floor(slots[0] - slots[2] * 0.1)
        # move NW corner up by 75% of chest height
        slots[1] = floor(slots[1] - slots[3] * 0.75)
        # expand width by 20%
        slots[2] = ceil(slots[2] * 1.2)
        # reduce height by 40%
        slots[3] = ceil(slots[3] * 0.60)

        slots = screenshot.crop(
            (slots[0], slots[1], slots[0] + slots[2], slots[1] + slots[3])
        )

        if self.debug and "slots" in self.debug:
            output_path = os.path.join(self.path, "output", f"slots.png")
            write_image(output_path, slots)

        return slots

    def _find_individual_slots(self, slots: Image):
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

            if self.debug and "slot" in self.debug:
                output_path = os.path.join(self.path, "output", f"slot.png")
                write_image(output_path, slot)

        return individual_slots

    def identify_gem(self, image: Image):
        resized_image = image.resize((50, 50), resample=Image.Resampling.NEAREST)
        resized_array = array(resized_image)
        input_array = array([resized_array])
        prediction = self.model.predict(input_array, verbose=0).tolist()[0]

        result = (self.categories[prediction.index(max(prediction))], max(prediction))

        if self.debug and "gems" in self.debug:
            create_dir(os.path.join(self.path, "output", result[0]))
            output_path = os.path.join(self.path, "output", result[0], "gems.png")
            write_image(output_path, image)
        elif self.debug and "tgems" in self.debug and result[0] in self.tgems:
            create_dir(os.path.join(self.path, "output", result[0]))
            output_path = os.path.join(self.path, "output", result[0], "tgems.png")
            write_image(output_path, image)

        return result

    def identify_gems(self, images: list):
        results = [self.identify_gem(x) for x in images]
        return results

    def identify(self, screenshot: Image):
        slots = self._find_slots(screenshot)
        slots = self._find_individual_slots(slots)
        gems = self.identify_gems(slots)
        return gems
