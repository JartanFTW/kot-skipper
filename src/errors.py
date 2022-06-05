class ChestNotFoundException(Exception):
    def __init__(self, process: str):
        self.err = "Failed to locate chest while " + process
        super().__init__(self.err)


class SkipNotFoundException(Exception):
    def __init__(self):
        self.err = "Failed to locate skip button"
        super().__init__(self.err)


class GoldRecognitionFailureException(Exception):
    def __init__(self):
        self.err = "Failed to identify gold count"
        super().__init__(self.err)


class SameDungeonException(Exception):
    def __init__(self):
        self.err = "Dungeon same as last dungeon"
