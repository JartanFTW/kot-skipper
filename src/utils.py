import os


def write_file(path, content):
    counter = 0

    while os.path.isfile(path):
        counter += 1
        path = os.path.splitext(path)[0] + f" ({counter})" + os.path.splitext(path)[1]

    with open(path, "w") as file:
        file.write(content)


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
