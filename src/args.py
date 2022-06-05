import argparse


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
        default=1,
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
