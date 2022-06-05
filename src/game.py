from io import BytesIO
import os

from adb_shell.adb_device import AdbDeviceTcp, _FileSyncTransactionInfo
from PIL import Image
from pyscreeze import locate

from .utils import write_file
from .errors import SkipNotFoundException


class GameManager:
    def __init__(self, path, ip="127.0.0.1", port=5555, debug=None):
        self.path = path
        self.debug = debug

        self.game = AdbDeviceTcp(ip, port)
        self.game.connect()

        self.skip_img = Image.open(os.path.join(path, "assets", "skip.png"))

        self._skip_location = None

    # def _screenshot_window(window) -> Image:
    # https://stackoverflow.com/a/24352388

    # dimensions = GetWindowRect(window)

    # hwndDC = GetWindowDC(window)
    # mfcDC = CreateDCFromHandle(hwndDC)
    # saveDC = mfcDC.CreateCompatibleDC()

    # saveBitMap = CreateBitmap()
    # saveBitMap.CreateCompatibleBitmap(
    #     mfcDC, dimensions[2] - dimensions[0], dimensions[3] - dimensions[1]
    # )

    # saveDC.SelectObject(saveBitMap)

    # windll.user32.PrintWindow(window, saveDC.GetSafeHdc(), 0)

    # bmpinfo = saveBitMap.GetInfo()
    # bmpstr = saveBitMap.GetBitmapBits(True)

    # image = Image.frombuffer(
    #     "RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1
    # )

    # DeleteObject(saveBitMap.GetHandle())
    # saveDC.DeleteDC()
    # mfcDC.DeleteDC()
    # ReleaseDC(window, hwndDC)

    # return image

    def screenshot(self) -> Image:
        bytes = BytesIO()

        self.game.shell("screencap /sdcard/screen.png")
        adb_info = self.game._open(b"sync:", None, 10.0, None)
        filesync_info = _FileSyncTransactionInfo(b"<2I", maxdata=2048)

        try:
            self.game._pull("/sdcard/screen.png", bytes, None, adb_info, filesync_info)
        finally:
            self.game._clse(adb_info)

        image = Image.open(bytes).convert("RGB")

        if self.debug and "window" in self.debug:
            output_path = os.path.join(self.path, "output", "window.png")
            write_file(output_path)

        self._last_screenshot = image
        return image

    def skip(self):

        if not self._skip_location:
            self._skip_location = locate(
                self.skip_img, self._last_screenshot, confidence=0.7
            )

            if not self._skip_location:
                screenshot = self.screenshot()
                _skip_location = locate(self.skip_img, screenshot, confidence=0.7)

            if not self._skip_location:
                raise SkipNotFoundException()

            self._skip_location = (
                self._skip_location[0] + int(self._skip_location[2] / 2),
                self._skip_location[1] + int(self._skip_location[3] / 2),
            )

        self.game.shell(
            f"input touchscreen tap {self._skip_location[0]} {self._skip_location[1]}"
        )
