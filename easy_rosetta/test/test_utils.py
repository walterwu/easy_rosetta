import os

def get_dirs(path):
    contents = os.listdir(path)
    dirs = []
    for item in contents:
        if os.path.isdir(os.path.join(path, item)):
            dirs.append(os.path.basename(item))
    return dirs

def get_files(path):
    contents = os.listdir(path)
    files = []
    for item in contents:
        if os.path.isfile(os.path.join(path, item)):
            files.append(os.path.basename(item))
    return files

