# Standard
import os
import sys
from time import sleep

# Third Party

# Local
from src.args import parse_arguments
from src.errors import (
    ChestNotFoundException,
    GoldRecognitionFailureException,
    SameDungeonException,
)
from src.game import GameManager
from src.gems import GemIdentifier
from src.gold import GoldIdentifier


def setup():
    global ARGS, PATH, last_gold

    if getattr(sys, "frozen", False):  # handles compiled to exe
        PATH = os.path.dirname(sys.executable)
    else:
        PATH = os.path.dirname(os.path.abspath(__file__))

    ARGS = parse_arguments(sys.argv[1:])

    last_gold = 0


def scan_dungeon(game, gold_identifier, gem_identifier=None):
    """
    Scans dungeon for target gold and/or gems.
    If target gold is found, returns int
    If target gem is found, returns tuple (gem STR, confidence INT)
    Otherwise returns None

    """
    global last_gold

    screenshot = game.screenshot()

    gold = gold_identifier.identify(screenshot)

    if gold == last_gold:
        raise SameDungeonException

    last_gold = gold

    if gem_identifier:
        gems = gem_identifier.identify(screenshot)

    if ARGS.gold and gold >= ARGS.gold:
        return gold

    if gem_identifier:
        for gem in gems:
            if gem[0] in ARGS.gems:
                return gem


def main():
    print("Press CTRL + C on this console to exit at any time")

    setup()

    if ARGS.emulator == "bluestacks":
        game = GameManager(PATH, debug=ARGS.debug)

    gold_identifier = GoldIdentifier(PATH, debug=ARGS.debug)

    gem_identifier = None
    if ARGS.gems or (ARGS.debug and "screenshotmode" in ARGS.debug):
        gem_identifier = GemIdentifier(PATH, debug=ARGS.debug, target_gems=ARGS.gems)

    # debug screenshot mode
    if ARGS.debug and "screenshotmode" in ARGS.debug:
        try:
            while True:
                input("Press enter when a totem is visible")
                screenshot = game.screenshot()
                gold_identifier.identify(screenshot)
                gem_identifier.identify(screenshot)
        except KeyboardInterrupt:
            # prevents keyboardinterrupt causing normal program function to begin
            return

    # main loop
    retries = 0

    while True:
        if retries > ARGS.retries:
            game.skip()
            sleep(ARGS.delay)
            retries = 0

        try:
            result = scan_dungeon(game, gold_identifier, gem_identifier=gem_identifier)
        except (
            SameDungeonException,
            GoldRecognitionFailureException,
            ChestNotFoundException,
        ) as e:
            print(e.err + ((" - retry " + str(retries)) if retries else ""))
            retries += 1
            sleep(ARGS.delay)
            continue

        if not result:
            game.skip()
            sleep(ARGS.delay)

        elif isinstance(result, int):
            print(f"Dungeon gold {result} meets target gold")
            input("Press Enter to continue")
        elif isinstance(result, tuple):
            print(
                f"Dungeon gem {result[0]} with confidence {result[1]:.2f} meets target gem"
            )
            input("Press Enter to continue")


if __name__ == "__main__":
    main()
