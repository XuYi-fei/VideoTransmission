import os


def create_folder(*args) -> None:
    for path in args:
        if not os.path.exists(path):
            os.makedirs(path)
