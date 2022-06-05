import os


def get_available_output(path):
    next_path = path
    if os.path.isfile(path):
        file_name, file_extension = os.path.basename(path).split(".")
        file_path = os.path.dirname(path)
        i = 1
        next_path = os.path.join(
            file_path, file_name + f" ({str(i)})" + "." + file_extension
        )
        while os.path.isfile(next_path):
            i += 1
            next_path = os.path.join(
                file_path, file_name + f" ({str(i)})" + "." + file_extension
            )

    return next_path


def write_file(path, content, binary=False):

    path = get_available_output(path)

    mode = "w"
    if binary:
        mode += "b"

    with open(path, mode) as file:
        file.write(content)


def write_image(path, image):
    path = get_available_output(path)
    image.save(path)


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
