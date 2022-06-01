"""
Very simple program to point out any image files that aren't png files
"""

import os

PATH = os.getcwd()

SORTED = os.path.join(PATH, "sorted")


def recurse(path):
    for dir in os.listdir(path):
        dir_path = os.path.join(path, dir)
        if os.path.isdir(dir_path):
            recurse(dir_path)
            continue
        if not dir.endswith(".png"):
            print(f"Found bad file: {dir_path}")


recurse(SORTED)
input("Finished")
