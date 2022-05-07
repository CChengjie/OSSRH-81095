import os


def get_source(spath: str):
    file_list = []
    for path, dirs, files in os.walk(spath):
        file_list.extend(
            [os.path.join(os.path.relpath(path, spath), file).replace(".\\", '').replace("\\", '/') for file in
             files if
             not str(os.path.relpath(path, spath)).startswith('.git')])
    return file_list