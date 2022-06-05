from numpy import array
import os

from easyocr import Reader
from PIL import Image
from pyscreeze import locate

from .errors import ChestNotFoundException, GoldRecognitionFailureException
from .utils import write_file


class GoldIdentifier:
    def __init__(self, path: str, debug: list = None):
        self.path = path
        self.debug = debug
        self.chest = Image.open(os.path.join(path, "assets", "chest.png"))

        self.reader = Reader(["en"], gpu=False)

    def _best_result(self, results, type=None):
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

    def identify(self, screenshot: Image):
        chest = locate(self.chest, screenshot, grayscale=False, confidence=0.5)

        if not chest:
            raise ChestNotFoundException("identifying slots")

        chest = (
            *chest[:2],
            chest[0] + chest[2],
            chest[1] + chest[3],
        )

        chest = screenshot.crop(chest)

        if self.debug and "chest" in self.debug:
            output_path = os.path.join(self.path, "output", f"chest.png")
            write_file(output_path, chest)

        chest_array = array(chest)
        results = self.reader.readtext(
            chest_array, allowlist="0123456789", low_text=0.5, width_ths=0.3
        )
        result = self._best_result(results, type=int)

        if not result:
            raise GoldRecognitionFailureException()

        return int(result[0])
